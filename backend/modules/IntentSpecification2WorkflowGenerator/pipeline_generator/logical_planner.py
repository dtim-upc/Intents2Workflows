import itertools
import uuid
from rdflib import Graph, URIRef
from tqdm import tqdm
from typing import Dict, List, Set, Tuple
import random
import math

from common import *
from graph_queries import intent_queries, ontology_queries, shape_queries, data_queries


def transform(ontology, implementation, data_graph, dataset_id, affected_columns:List[URIRef]):
    new_data_graph = Graph() +data_graph
    transformations = ontology_queries.get_implementation_transformations(ontology, implementation)
    colunm_str = " ".join(f"<{str(u)}>" for u in affected_columns)
    new_dataset_id = dataset_id
    #tqdm.write(f"Executing transformations for {implementation} with columns {affected_columns}")
    for t in transformations:
        rendered_t = t.replace("$$COLUMNS_TO_TRANSFORM$$", colunm_str)
        #print(rendered_t)
        new_dataset_id = hash((new_dataset_id, rendered_t))
        new_data_graph.update(rendered_t)
    return new_data_graph, new_dataset_id

def satisfies_shape(data_graph, ontology, shape, dataset):
    cols = set()

    if shape_queries.iscolumnar(ontology, shape):
        columns = data_queries.get_dataset_columns_uri(data_graph, dataset)
        unsatisfied_shapes = shape_queries.get_nodes_that_NOT_satisfy_shape(data_graph, ontology, shape, focus_nodes=columns)
        cols = unsatisfied_shapes
    else:
        unsatisfied_shapes = shape_queries.get_nodes_that_NOT_satisfy_shape(data_graph, ontology, shape, focus_nodes=[dataset])
    
    return len(unsatisfied_shapes) == 0, cols
        


logical_plans_cahce = {}
def produce_plans(ontology:Graph, shape_graph:Graph, data_graph:Graph, dataset:URIRef, dataset_id, unsatisfied_shapes:List[Tuple[URIRef, List[URIRef]]], max_imp_level, loop_shapes:Set[URIRef]):

    if len(unsatisfied_shapes) == 0 or unsatisfied_shapes is None:
        yield [], data_graph
        return
    
    shape_satisfied = True
    cols = set()
    unsatisfied_shape = None

    while shape_satisfied and len(unsatisfied_shapes) > 0:
        unsatisfied_shape = unsatisfied_shapes.pop()
        shape_satisfied, cols = satisfies_shape(data_graph, ontology, unsatisfied_shape, dataset)

    if shape_satisfied:
        tqdm.write(f"Data ALREADY satisfies {unsatisfied_shape}.")
        yield [], data_graph
        return

    first = unsatisfied_shape
    tqdm.write(f"Creating plan for {first}") 

    transformer_cols = set(cols)
    first_loop_shapes = loop_shapes | {first}
    implementations = find_implementations_to_satisfy_shape_constrained(ontology, shape_graph, first, exclude_appliers=True)

    for implementation in implementations:
        key = (implementation, dataset_id)

        cached_plan = implementations_from_shape_cache.get(key)
        if  cached_plan is not None:
            tqdm.write(f"SUPERHIT! with implementation {implementation}")
            first_plans_generator = cached_plan

        else:
            first_plans_generator = list(get_implementation_prerquisites(ontology, shape_graph, data_graph, dataset, dataset_id, implementation, max_imp_level, affected_columns=transformer_cols, loop_shapes=first_loop_shapes))
            implementations_from_shape_cache[key] = first_plans_generator
        
        for first_plan_generator in first_plans_generator:
            if first_plan_generator is None:
                continue

            first_plan, (transformed_data, data_id) = first_plan_generator
            rest_plans_generator = produce_plans(ontology, shape_graph, transformed_data, dataset, data_id, set(unsatisfied_shapes), max_imp_level, loop_shapes=loop_shapes)

            for rest_plan_generator in rest_plans_generator:
                if rest_plan_generator is None:
                    continue

                rest_plan, rest_data = rest_plan_generator
                complete_plan = [] + first_plan
                complete_plan.extend(rest_plan)
                #tqdm.write(f"Produced plan: {complete_plan}")
                yield complete_plan, rest_data
     


def get_implementation_prerquisites(ontology: Graph, shape_graph: Graph, data_graph:Graph, dataset:URIRef, dataset_id, implementation, max_imp_level:int, log: bool = False, depth = 0, 
                                    loop_shapes = set(), affected_columns = set()):
    
    if log:
        tqdm.write("Recursive: " + str(implementation.fragment) + " " + str(affected_columns))
    
    inputs = ontology_queries.get_implementation_input_specs(ontology, implementation, max_imp_level)
    shapes_to_satisfy = set(get_io_shapes(ontology, inputs))

    if shapes_to_satisfy & loop_shapes:
        tqdm.write(f"Preventing a loop with shape")
        yield None
        return
    
    previous_shapes = set(loop_shapes)
    produced_plans = produce_plans(ontology, shape_graph, data_graph, dataset, dataset_id, shapes_to_satisfy, max_imp_level, loop_shapes=previous_shapes)
        
    for pp in produced_plans:
        if pp is None:
            continue

        #print("pp", pp)

        plan, data = pp
        dataset_cols = set(data_queries.get_dataset_columns_uri(data, dataset))
        remaining_affected_colums = list(affected_columns & dataset_cols)

        result =  plan + [(implementation, remaining_affected_colums)], transform(ontology, implementation, data, dataset_id, remaining_affected_colums)
        yield result

    



MAX_PLAN_LENGTH = 10

def get_reader_component(tensor_dataset:bool, dataset_format:URIRef):
    component_name = f"component-{dataset_format.lower()}_reader_component"
    if tensor_dataset:
        component_name +="_(tensor)"
    return cb[component_name]

def get_writer_component(tensor_dataset:bool): #TODO dynamically obtain those components
    if tensor_dataset:
        return cb["component-data_writer_component"] #this is redundant (or maybe should be different?) 
    else:
        return cb["component-data_writer_component"]

def get_partition_component():
    return cb["component-data_partition_component"]

def get_io_shapes(ontology: Graph,  ios: List[Tuple[URIRef,List[URIRef]]]):
    for i, (io_spec, io_shapes) in enumerate(ios):
        #for io_shape in io_shapes:
                    return io_shapes

implementations_from_shape_cache = {} 
def find_implementations_to_satisfy_shape_constrained(ontology: Graph, shape_graph:Graph, shape: URIRef, exclude_appliers: bool = False) -> List[URIRef]:

    cache_impls = implementations_from_shape_cache.get(shape)
    if cache_impls is not None:
        tqdm.write(f"HIT! with shape {shape}")
        return cache_impls
    
    pot_impl_unconstr = ontology_queries.find_implementations_to_satisfy_shape(ontology,shape,exclude_appliers)
    constr_shapes = shape_queries.reinforce_constraint(shape_graph,ontology,ab.ImplementationConstraint,pot_impl_unconstr)
    
    implementations_from_shape_cache[shape] = constr_shapes

    return constr_shapes

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
            if len(shape_queries.get_nodes_that_NOT_satisfy_shape(graph, graph, datatag, dataset))==0:
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
        return True
        
        temporal_graph = ontology #WARNING: temporal_graph is just an alias. Ontology is modified.

        main_component:URIRef = combination[-1][0]
        workflow_name = f'workflow_{main_component.fragment}'
        workflow = tb.term(workflow_name)
        temporal_graph.add((workflow, RDF.type, tb.Workflow))
        
        triples_to_add = []

        for component, cols in combination: 
            triples_to_add.append((workflow, tb.hasComponent, component, temporal_graph))  
        
        temporal_graph.addN(triples_to_add)

        valid = len(shape_queries.get_nodes_that_NOT_satisfy_shape(temporal_graph, shape_graph, shape=[ab.WorkflowConstraint], focus_nodes=[workflow])) == 0
        temporal_graph.remove((workflow, RDF.type, tb.Workflow))
        for triple in triples_to_add:
            temporal_graph.remove(triple[:-1])
        return valid

def materialize_plan(ontology, shape_graph, dataset, component_threshold, task, plan):
    plan_comb = []
    total_comb = 1
    #tqdm.write(f"Materializing {plan}")

    for (impl, cols) in plan:
        available_components = ontology_queries.get_components_from_abstract_implementation(ontology, impl)
        if len(available_components) == 0:
            available_components = ontology_queries.get_implementation_components(ontology, impl)
        """ if (impl, RDF.type, tb.AbstractImplementation) in ontology:
            specific_implementations = ontology.objects(impl, tb.hasSpecificImplementation)
        else:
            specific_implementations = [impl]
        
        components = []
        for specific_impl in specific_implementations:
            available_components = get_implementation_components_constrained(ontology, shape_graph, specific_impl)
            best_components = available_components #list(get_best_components(ontology, task, available_components, dataset, component_threshold).keys())
            components.extend([(c,cols) for c in best_components]) """
        
        components = [(c,cols) for c in available_components]
        plan_comb.append(components)
        total_comb *= len(components)

    return itertools.product(*plan_comb), total_comb

    


import time

def component_comb_to_logical_plan(ontology: Graph, component_combination: Tuple[URIRef], requires_partition:bool, reader_component:URIRef, writer_component:URIRef, partition_component:URIRef):
    logical_plan = {}
    applier_list = []
    component_list = list(component_combination) 
    plan_order = []
    component_cols = {}

    logical_plan[reader_component] = [f"{0}--{component_list[0][0]}"]
    last_not_applier = reader_component
    last_applier = None
    plan_order.append(reader_component)

    for i, (component, cols) in enumerate(component_list):
        applier = ontology_queries.get_applier(ontology, component)
        component_name = f"{i}--{component}"
        dep = []
        
        if (i+1) < len(component_list):
            next = component_list[i+1][0]
            dep.append(f"{i+1}--{next}")

        if requires_partition and applier is not None:

            applier_name = f"{i}--{applier}"

            dep.append(applier_name)
            applier_list.append(applier_name)

            logical_plan[component_name] = dep 
            plan_order.append(component_name)
            last_applier=component_name

            component_cols[component_name] = cols
            component_cols[applier_name] = cols


        else:
            if last_applier is not None:
                logical_plan[last_applier] = dep
                logical_plan[component_name] = logical_plan[last_not_applier]
                logical_plan[last_not_applier] = [component_name]
            
            else:
                logical_plan[component_name] = dep

            component_index = plan_order.index(last_not_applier)
            last_not_applier = component_name
            plan_order.insert(component_index+1,component_name) 
            component_cols[component_name] = cols

    #print("sense partition", logical_plan, plan_order)
        


    if requires_partition:
        logical_plan[partition_component] = logical_plan[last_not_applier]
        logical_plan[last_not_applier] = [partition_component]
        component_index = plan_order.index(last_not_applier)
        last_not_applier = partition_component
        plan_order.insert(component_index+1,partition_component)
        #print("amb partition", logical_plan, plan_order)


    for i, a in enumerate(applier_list):
        if (i+1) < len(applier_list):
            logical_plan[a] = [applier_list[i+1]]
        else:
            logical_plan[a] = []
        plan_order.append(a)
    
    if not last_not_applier is None and len(applier_list) > 0:
        logical_plan[last_not_applier].append(applier_list[0])

    logical_plan[plan_order[-1]].append(writer_component)
    logical_plan[writer_component] = []
    plan_order.append(writer_component)

    return logical_plan, plan_order, component_cols
 

def generate_logical_plans(ontology: Graph, shape_graph: Graph, intent_graph: Graph, data_graph:Graph, pot_impls, log: bool = False) -> Dict[str,Dict[URIRef,List[URIRef]]]:
    start = time.perf_counter()
    intent_iri = intent_queries.get_intent_iri(intent_graph=intent_graph)
    dataset, task, algorithm = intent_queries.get_intent_dataset_task(intent_graph, intent_iri) 
    is_tensor = data_queries.isTensor_data(data_graph, dataset)
    dataset_format = data_queries.get_dataset_format(data_graph, dataset)
    reader_component = get_reader_component(is_tensor, dataset_format)
    writer_component = get_writer_component(is_tensor)
    partition_component = get_partition_component()
    requires_partition = task in  [cb.SupervisedLearning, cb.Classification, cb.Regression]

    component_threshold = intent_queries.get_component_threshold(intent_graph, intent_iri)
    max_imp_level = intent_queries.get_max_importance_level(intent_graph, intent_iri)

    if log:
        tqdm.write(f'Preprocessing Component Percentage Threshold: {component_threshold*100}%')
        tqdm.write(f'Maximum complexity level: {max_imp_level}')
        tqdm.write('-------------------------------------------------')

    options = []
    combs = 0
    end =  time.perf_counter()
    tqdm.write(f"Treball previ: {end-start}")
    
    for imp in pot_impls:
        #result, comb = get_implementation_prerquisites(ontology, shape_graph, data_graph, dataset, imp, max_imp_level, log=log, inherited_satisfied_shapes=[])
        result = get_implementation_prerquisites(ontology, shape_graph, data_graph, dataset, hash(dataset),imp, max_imp_level, log=log)

        if not result is None and result != []:
            options.append(result)
            combs += 1
   
    
    logical_plans = []
    counter = {}


    for transformation_combination in tqdm(options, total=combs,desc='Implementation combinations', position=0, leave=False):
        tant = time.perf_counter()
        
        for tc, data in tqdm(transformation_combination,desc='Implementation combinations', position=0, leave=False):
            start = time.perf_counter()
            tqdm.write(f"Tc generated in {start-tant}")
            component_combinations, total_comb = materialize_plan(ontology, shape_graph, dataset, component_threshold, task, tc)
            end = time.perf_counter()
            tqdm.write(f"Tc materialized in {end-start}")

            startb = time.perf_counter()

            for component_combination in tqdm(component_combinations, total=total_comb, desc='Component combinations', position=1, leave=False):

                #tqdm.write(f"creating {component_combination}")
                start = time.perf_counter()
                tqdm.write(f"Tcc generated in {start-startb}")

                startctl = time.perf_counter()
                if  is_valid_workflow_combination(ontology, shape_graph, component_combination):
                    endctl = time.perf_counter()
                    tqdm.write(f"ivwc generated in {endctl-startctl}")
                    
                    logical_plan, order, component_cols = component_comb_to_logical_plan(ontology, component_combination, requires_partition, reader_component, writer_component, partition_component)
                    
                    main_component = URIRef(component_combination[-1][0]).fragment

                    if main_component not in counter:
                        counter[main_component] = 0

                    plan_name = f'{main_component.split("-")[1].replace("_", " ").replace(" learner", "").title()} {counter[main_component]}'
                    logical_plans.append({"name":plan_name, "plan":[(key, logical_plan[key]) for key in order], "cols":component_cols})
                    
                    counter[main_component] += 1
                end = time.perf_counter()
                tqdm.write(f"Tcc materialized in {end-start}")
                startb = time.perf_counter()
            tant = time.perf_counter()
        


    #t2 = time.time()
    #print("Temps total",t2-t)
    return {"logical_plans": logical_plans}
    
