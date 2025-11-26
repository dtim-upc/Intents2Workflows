import itertools
import uuid
from rdflib import Graph, URIRef
from tqdm import tqdm
from typing import Dict, List, Tuple
import random
import math

from common import *
from graph_queries import intent_queries, ontology_queries, shape_queries, data_queries


MAX_PLAN_LENGTH = 10

def get_reader_component(dataset_type:URIRef, dataset_format:URIRef):
    component_name = f"component-{dataset_format.lower()}_reader_component"
    if dataset_type == dmop.TensorDataset:
        component_name +="_(tensor)"
    return cb[component_name]

def get_writer_component(dataset_type:URIRef): #TODO dynamically obtain those components
    if dataset_type == dmop.TensorDataset:
        return cb["cb:component-data_writer_component_(tensor)"]
    else:
        return cb["component-data_writer_component"]

def get_io_shapes(ontology: Graph,  ios: List[Tuple[URIRef,List[URIRef]]]):
    for i, (io_spec, io_shapes) in enumerate(ios):
        for io_shape in io_shapes:
                    return io_shapes
        
def find_implementations_to_satisfy_shape_constrained(ontology: Graph, shape_graph:Graph, shape: URIRef, exclude_appliers: bool = False) -> List[URIRef]:
    pot_impl_unconstr = ontology_queries.find_implementations_to_satisfy_shape(ontology,shape,exclude_appliers)
    return shape_queries.reinforce_constraint(shape_graph,ontology,ab.ImplementationConstraint,pot_impl_unconstr)

def get_implementation_components_constrained(ontology: Graph, shape_graph: Graph, implementation: URIRef) -> List[URIRef]:
    pot_comp_unconstr = ontology_queries.get_implementation_components(ontology, implementation)
    return shape_queries.reinforce_constraint(shape_graph, ontology, ab.ComponentConstraint, pot_comp_unconstr)


def get_best_components(graph: Graph, task: URIRef, components: List[URIRef], dataset: URIRef, percentage: float = None):

    preferred_components = {}
    sorted_components = {}
    for component in components:
        
        component_rules = ontology_queries.retreive_component_rules(graph, task, component)
        score = 0

        preferred_components[component] = (score,1)

        for datatag, weight_rank in component_rules.items():
            rule_weight = weight_rank[0]
            component_rank = weight_rank[1]
            if shape_queries.satisfies_shape(graph, graph, datatag, dataset):
                score+=rule_weight
            else:
                score-=rule_weight
                
            preferred_components[component] = (score, component_rank)

    sorted_preferred = sorted(preferred_components.items(), key=lambda x: x[1][0], reverse=True)

    if len(sorted_preferred) > 0: ### there are multiple components to choose from
        best_scores = set([comp[1] for comp in sorted_preferred])
        if len(best_scores) == 1:
            sorted_preferred = random.sample(sorted_preferred, int(math.ceil(len(sorted_preferred)*percentage))) if percentage else sorted_preferred
        elif len(best_scores) > 1: ### checking if there is at least one superior component
            sorted_preferred = [x for x in sorted_preferred if x[1] >= sorted_preferred[0][1]]


    for comp, rules_nbr in sorted_preferred:
        sorted_components[comp] = rules_nbr 

    return sorted_components

def is_valid_workflow_combination(ontology:Graph, shape_graph:Graph, combination: List[URIRef]) -> bool:
        
        temporal_graph = ontology #WARNING: temporal_graph is just an alias. Ontology is modified.

        main_component:URIRef = combination[-1]
        workflow_name = f'workflow_{main_component.fragment}'
        workflow = tb.term(workflow_name)
        temporal_graph.add((workflow, RDF.type, tb.Workflow))
        
        triples_to_add = []

        for component in combination:
            triples_to_add.append((workflow, tb.hasComponent, component, temporal_graph))  
        
        temporal_graph.addN(triples_to_add)

        valid = shape_queries.satisfies_shape(temporal_graph, shape_graph, shape=ab.WorkflowConstraint, focus=workflow)
        temporal_graph.remove((workflow, RDF.type, tb.Workflow))
        for triple in triples_to_add:
            temporal_graph.remove(triple[:-1])
        return valid


def get_implementation_prerquisites(ontology: Graph, shape_graph: Graph, data_graph:Graph, dataset:URIRef, implementation, max_imp_level, log: bool = False, depth = 0):

    if log:
        tqdm.write("Recursive: " + str(implementation))
    
    inputs = ontology_queries.get_implementation_input_specs(ontology, implementation, max_imp_level)

    shapes_to_satisfy = get_io_shapes(ontology, inputs)

    if shapes_to_satisfy is None:
        shapes_to_satisfy = {}
    
    if log:
        tqdm.write(f'\tData input: {[x.fragment for x in shapes_to_satisfy]}')

    unsatisfied_shapes = [shape for shape in shapes_to_satisfy if
                            not shape_queries.satisfies_shape(data_graph, ontology, shape, dataset)]
    
    if log:
        tqdm.write(f'UNSATISFIED SHAPES: {unsatisfied_shapes}')

    if len(unsatisfied_shapes) > 0 and depth >= MAX_PLAN_LENGTH:
        if log:
            tqdm.write('MAX_DEPTH achieved')
        return None

    available_transformations = { shape: [] 
                                    for shape in unsatisfied_shapes}
    total_num_comb = 1
    for shape in unsatisfied_shapes:
        num_combs_impl = 0
        for imp in find_implementations_to_satisfy_shape_constrained(ontology, shape_graph, shape, exclude_appliers=True):

            if log:
                tqdm.write(f'Suitable implementation for {shape}: {imp}')

            transformations, num_comb = get_implementation_prerquisites(ontology, shape_graph, data_graph, dataset, imp, max_imp_level, log=log, depth=depth+1)
            if transformations is not None:
                available_transformations[shape].extend(transformations)
                num_combs_impl += num_comb

        if len(available_transformations[shape]) == 0:
            if log:
                tqdm.write("implementations not found")
            return None, 0
        total_num_comb = total_num_comb * num_combs_impl
        
    if log:
        tqdm.write(f'\tAvailable transformations: ')
        for shape, transformations in available_transformations.items():
            tqdm.write(f'\t\t{shape.fragment}: {[x for x in transformations]}')

    if len(unsatisfied_shapes) > 0 and len(available_transformations) > 0:
        transformation_combinations =  itertools.product(*available_transformations.values(),[implementation])
    elif len(unsatisfied_shapes) > 0:
        return None, 0
    else:  
        transformation_combinations = [implementation]
        total_num_comb = 1
    
    return transformation_combinations, total_num_comb
    
def get_prep_comp(ontology, shape_graph, dataset, component_threshold, task, plan):
    if isinstance(plan, URIRef):
        available_components = get_implementation_components_constrained(ontology, shape_graph, plan)
        #print(f"available_components of {plan}:",available_components)
        best_components = get_best_components(ontology, task, available_components, dataset, component_threshold)
        return [list(best_components.keys())], len(best_components.keys())
    else: #tuple
        elms = []
        total_comb = 1
        for element in plan:
            comp_list, num_comb = get_prep_comp(ontology, shape_graph, dataset, component_threshold, task,element)
            elms.extend(comp_list)
            total_comb = total_comb * num_comb
        return elms, total_comb


import time   

def component_comb_to_logical_plan(ontology: Graph, component_combination: Tuple[URIRef], reader_component:URIRef, writer_component:URIRef):
    logical_plan = {}
    applier_list = []
    component_list = list(component_combination)
    last_not_applier = component_list[0] if len(component_list) > 0 else None

    logical_plan[reader_component] = [component_list[0]]

    for i, component in enumerate(component_list):
        dep = []

        if (i+1) < len(component_combination):
            next = component_combination[i+1]
            dep.append(next)

        applier = ontology_queries.get_applier(ontology, component)

        if applier is not None:
            dep.append(applier)
            applier_list.append(applier)
        else:
            last_not_applier = component
        
        logical_plan[component] = dep #Assuming python 3.7+ to guarantee that dict order


    for i, a in enumerate(applier_list):
        if (i+1) < len(applier_list):
            logical_plan[a] = [applier_list[i+1]]
        else:
            logical_plan[a] = []
    
    if not last_not_applier is None:
        logical_plan[last_not_applier].append(applier_list[0])

    logical_plan[list(logical_plan.keys())[-1]].append(writer_component)
    logical_plan[writer_component] = []

    return logical_plan


def generate_logical_plans(ontology: Graph, shape_graph: Graph, intent_graph: Graph, data_graph:Graph, pot_impls, log: bool = False) -> Dict[str,Dict[URIRef,List[URIRef]]]:
    t = time.time()
    intent_iri = intent_queries.get_intent_iri(intent_graph=intent_graph)
    dataset, task, algorithm = intent_queries.get_intent_dataset_task(intent_graph, intent_iri) 
    dataset_type = data_queries.get_dataset_type(data_graph, dataset)
    dataset_format = data_queries.get_dataset_format(data_graph, dataset)
    reader_component = get_reader_component(dataset_type, dataset_format)
    writer_component = get_writer_component(dataset_type)

    component_threshold = intent_queries.get_component_threshold(intent_graph, intent_iri)
    max_imp_level = intent_queries.get_max_importance_level(intent_graph, intent_iri)

    if log:
        tqdm.write(f'Preprocessing Component Percentage Threshold: {component_threshold*100}%')
        tqdm.write(f'Maximum complexity level: {max_imp_level}')
        tqdm.write('-------------------------------------------------')

    options = []
    combs = 0
    for imp in pot_impls:
        result, comb = get_implementation_prerquisites(ontology, shape_graph, data_graph, dataset, imp, max_imp_level, log=log)
        if not result is None and result != []:
            options.append(result)
            combs += comb
   
    
    logical_plans = []
    counter = {}
    t_comb = 0


    for transformation_combination in tqdm(options, total=combs,desc='Implementation combinations', position=0, leave=False):
        
        for tc in transformation_combination:
            prep_components, comp_comb = get_prep_comp(ontology, shape_graph, dataset, component_threshold, task, tc)
            t_comb += comp_comb
            component_combinations = itertools.product(*prep_components)
            

            for component_combination in tqdm(component_combinations, total=comp_comb,desc='Component combinations', position=1, leave=False):

                if  is_valid_workflow_combination(ontology, shape_graph, component_combination):
                    logical_plan = component_comb_to_logical_plan(ontology, component_combination, reader_component, writer_component)
                    main_component = URIRef(component_combination[-1]).fragment

                    if main_component not in counter:
                        counter[main_component] = 0

                    plan_name = f'{main_component.split("-")[1].replace("_", " ").replace(" learner", "").title()} {counter[main_component]}'
                    logical_plans.append({"name":plan_name, "plan":[(key, value) for key, value in logical_plan.items()]})
                    
                    counter[main_component] += 1

    t2 = time.time()
    print("Temps total",t2-t)
    return {"logical_plans": logical_plans}
    
