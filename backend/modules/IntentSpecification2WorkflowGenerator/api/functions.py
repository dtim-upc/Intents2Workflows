import zipfile
import sys
import os

from rdflib.term import Node

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from pipeline_generator.optimized_pipeline_generator import *

def get_custom_ontology(path):
    graph = get_graph_xp()
    ontologies = [
        r'ontologies/tbox.ttl',
        r'ontologies/cbox.ttl',
        r'ontologies/abox.ttl',
        path
    ]
    for o in ontologies:
        graph.parse(o, format="turtle")

    DeductiveClosure(OWLRL_Semantics).expand(graph)
    return graph

def get_custom_ontology_only_problems():
    graph = get_graph_xp()
    ontologies = [
        r'ontologies/tbox.ttl',
        r'ontologies/cbox.ttl',
        r'ontologies/abox.ttl',
    ]
    for o in ontologies:
        graph.parse(o, format="turtle")

    DeductiveClosure(OWLRL_Semantics).expand(graph)
    return graph

def get_intent_name(plan_graph:Graph) -> str:
    intent_iri = get_intent_iri(plan_graph)
    return intent_iri.fragment

def connect_algorithms(ontology, shape_graph, algos_list):
    impls_algos = {imp : algo + "-Train" if "learner" in imp.fragment else algo
                   for algo in algos_list for imp in get_potential_implementations_constrained(ontology, shape_graph, algo,exclude_appliers=False)}
    print(impls_algos)

    linked_impls = {}

    impls_list = list(impls_algos.keys())
    
    for preceding_impl in impls_list:
        following_impls = impls_list

        out_specs = get_implementation_output_specs(ontology, preceding_impl)
        out_spec_set = {out_sp for out_spec in out_specs for out_sp in out_spec}

        preceding_impl_key = impls_algos[preceding_impl]
        linked_impls.setdefault(preceding_impl_key, [])
        
        for following_impl in following_impls:

            in_specs = get_implementation_input_specs(ontology, following_impl)
            in_spec_set = {in_sp for in_spec in in_specs for in_sp in in_spec}

            if out_spec_set & in_spec_set:
                following_impl_key = impls_algos[following_impl]

                if following_impl_key not in linked_impls[preceding_impl_key]:
                    linked_impls[preceding_impl_key].append(following_impl_key)

    return linked_impls



def abstract_planner(ontology: Graph, shape_graph: Graph, intent: Graph) -> Tuple[
    Dict[Node, Dict[Node, List[Node]]], Dict[Node, List[Node]]]:

    dataset, task, algorithm, intent_iri = get_intent_info(intent)

    algs = [algorithm] if algorithm is not None else get_algorithms_from_task_constrained(ontology, shape_graph, task)

    print(algs)

    impls = []
    for al in algs:
        print(get_potential_implementations_constrained(ontology, shape_graph, al))
        impls.append(get_potential_implementations_constrained(ontology, shape_graph, al))
    
    print(impls)

    algs_shapes = {}
    alg_plans = {alg: [] for alg in algs}
    available_algs = [] # to make sure abstract plans are only made for algorithms with at least one available implementation
    for impl in impls:
        if len(impl) > 0:
            alg = next(ontology.objects(impl[0], tb.implements)), 
            (impl[0], RDF.type, tb.Implementation) in ontology and (tb.ApplierImplementation not in ontology.objects(impl[0], RDF.type))

            algs_shapes[alg[0]] = get_implementation_input_specs(ontology, impl[0])[0] #assuming data shapes is on input 0

            alg_plans[alg[0]].extend(impl)

            available_algs.append(alg[0])
    
    plans = {}
    #print(algs_shapes)
    for alg in available_algs:
        if cb.TrainTabularDatasetShape in algs_shapes[alg]:
            plans[alg] = connect_algorithms(ontology, shape_graph,[cb.DataLoading, cb.Partitioning, alg, cb.DataStoring])
        else:
            plans[alg] = connect_algorithms(ontology, shape_graph, [cb.DataLoading, alg])
    #print(plans)
    return plans, alg_plans
    

def workflow_planner(ontology: Graph, shape_graph: Graph, implementations: List, intent: Graph):
    dataset, task, algorithm, intent_iri = get_intent_info(intent)

    component_threshold = next(intent.objects(intent_iri, tb.has_component_threshold), None)

    print(implementations)

    impls_with_shapes = [
        (implementation, get_implementation_input_specs(ontology, implementation))
        for implementation in implementations]

    components = [
        (c, impl, inputs)
        for impl, inputs in impls_with_shapes
        for c in get_implementation_components_constrained(ontology, shape_graph, impl)
    ]

    workflow_order = 0

    workflows = []

    for component, implementation, inputs in tqdm(components, desc='Components', position=1):
        shapes_to_satisfy = identify_data_io(ontology, inputs)
        assert shapes_to_satisfy is not None and len(shapes_to_satisfy) > 0

        unsatisfied_shapes = [shape for shape in shapes_to_satisfy if
                              not satisfies_shape(ontology, ontology, shape, dataset)]

        available_transformations = {
            shape: get_implementation_components_constrained(ontology, shape_graph, imp)
            for shape in unsatisfied_shapes
            for imp in find_implementations_to_satisfy_shape_constrained(ontology, shape_graph, shape, exclude_appliers=True)
        }

        for transformation, methods in available_transformations.items():
            best_components = get_best_components(ontology, task, methods, dataset, float(component_threshold)/100.0)

            available_transformations[transformation] = list(best_components.keys())


        transformation_combinations = list(
            enumerate(itertools.product(*available_transformations.values())))
        

        transformation_combinations_constrained = prune_workflow_combinations(ontology, shape_graph, transformation_combinations,component)

        for i, transformation_combination in tqdm(transformation_combinations_constrained, desc='Transformations', position=0,
                                                  leave=False):
            workflow_name = f'workflow_{workflow_order}_{intent_iri.fragment}_{uuid.uuid4()}'.replace('-', '_')
            wg, w = build_general_workflow(workflow_name, ontology, dataset, component,
                                           transformation_combination, intent) 

            wg.add((w, tb.generatedFor, intent_iri))
            wg.add((intent_iri, RDF.type, tb.Intent))
            wg += shape_graph

            workflows.append(wg)
            workflow_order += 1
    return workflows


def logical_planner(ontology: Graph, workflow_plans: List[Graph]):
    logical_plans = {}
    mapper = {}
    counter = {}
    for workflow_plan in workflow_plans:
        steps = list(workflow_plan.subjects(RDF.type, tb.Step))
        step_components = {step: next(workflow_plan.objects(step, tb.runs)) for step in steps}
        step_next = {step: list(workflow_plan.objects(step, tb.followedBy)) for step in steps}
        logical_plan = {
            step_components[step]: [step_components[s] for s in nexts] for step, nexts in step_next.items()
        }
        main_component = next((comp for comp in logical_plan.keys() 
                      if logical_plan[comp] == [cb.term('component-csv_local_writer')] 
                      or logical_plan[comp] == []), None)
        if (main_component, RDF.type, tb.ApplierImplementation) in ontology:
            options = list(ontology.objects(main_component, tb.hasLearner))
            main_component = next(o for o in options if (None, None, o) in workflow_plan)
        if main_component not in counter:
            counter[main_component] = 0
        plan_id = (f'{main_component.fragment.split("-")[1].replace("_", " ").replace(" learner", "").title()} '
                   f'{counter[main_component]}')
        counter[main_component] += 1
        logical_plans[plan_id] = logical_plan
        mapper[plan_id] = workflow_plan

    return logical_plans, mapper

def logical_planner_extremexp(ontology: Graph, workflow_plans: List[Graph]):
    logical_plans = {}
    counter = {}
    tasks = []
    extremexp_workflows = []
    workflow_counter = 0
    for workflow_plan in workflow_plans:
        steps = list(workflow_plan.subjects(RDF.type, tb.Step))
        step_components = {step: next(workflow_plan.objects(step, tb.runs)) for step in steps}
        step_next = {step: list(workflow_plan.objects(step, tb.followedBy)) for step in steps}
        logical_plan = {
            step_components[step]: [step_components[s] for s in nexts] for step, nexts in step_next.items()
        }

        workflow_name = "Workflow_" + str(workflow_counter)
        workflow_counter += 1
        extremexp_workflow = generate_extremexp_workflow(ontology, logical_plan, tasks, workflow_name)
        extremexp_workflows.append(extremexp_workflow)

        main_component = next(
            comp for comp in logical_plan.keys() if logical_plan[comp] == [cb.term('component-csv_local_writer')])
        if (main_component, RDF.type, tb.ApplierImplementation) in ontology:
            options = list(ontology.objects(main_component, tb.hasLearner))
            main_component = next(o for o in options if (None, None, o) in workflow_plan)
        if main_component not in counter:
            counter[main_component] = 0
        plan_id = (f'{main_component.fragment.split("-")[1].replace("_", " ").replace(" learner", "").title()} '
                   f'{counter[main_component]}')
        counter[main_component] += 1
        logical_plans[plan_id] = {"logical_plan": logical_plan, "graph": workflow_plan.serialize(format="turtle")}

    tasks = list(dict.fromkeys(tasks))  # remove duplicates

    return logical_plans, extremexp_workflows, tasks

def generate_extremexp_workflow(ontology, logical_plan, tasks, workflow_name):
    workflow = {}
    workflow["workflow_name"] = workflow_name
    task_implementations = {}
    query_template = """ PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                                SELECT ?implementation ?implements
                                WHERE {{
                                    <{key}> tb:hasImplementation ?implementation .
                                    ?implementation tb:implements ?implements .
                                }} """

    if len(tasks) == 0: # Build task array
        for key in logical_plan.keys():
            query_execute = query_template.format(key=key)
            results = ontology.query(query_execute)
            for row in results:
                if "learner" in row.implementation:
                    tasks.append("ModelTrain")
                elif "predictor" in row.implementation:
                    tasks.append("ModelPredict")
                else:
                    tasks.append(row.implements[row.implements.find('#') + 1:])

    for key in logical_plan.keys():
        query_execute = query_template.format(key=key)
        results = ontology.query(query_execute)
        for row in results:
            if "applier" not in key:
                task = row.implements[row.implements.find('#') + 1:]
                if "learner" in row.implementation:
                    task = "ModelTrain"
                elif "predictor" in row.implementation:
                    task = "ModelPredict"
                task_implementations[task] = "tasks/intent_name/" + key[key.find('-') + 1:] + ".py"
            # print(f"Key: {key}, implementation: {row.implementation}, implements: {row.implements}")

    workflow["task_implementations"] = task_implementations
    workflow["experiment_space_name"] = "S_" + workflow_name
    workflow["experiment_space"] = []
    return workflow

def compress(folder: str, destination: str) -> None:
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                archive_path = os.path.relpath(file_path, folder)
                zipf.write(file_path, arcname=os.path.join(os.path.basename(folder), archive_path))
