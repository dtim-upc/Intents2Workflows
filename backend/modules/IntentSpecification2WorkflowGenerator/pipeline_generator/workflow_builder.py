from typing import Dict, List, Tuple, Set
import uuid
from rdflib import Graph, URIRef, Literal, BNode
from tqdm import tqdm
from graph_queries import ontology_queries, intent_queries, data_queries
from .utils.dataset import Dataset
from .utils.transformation_engine import run_component_transformation
from common import *
import time

def get_port_target_type(shapes:List[URIRef]):

    if len(shapes) == 0:
        return False, False
    
    model_port = shapes[0] in model_shapes #only one is enough, as model ports only have one shape that targets model

    """for s in shapes:
        data_port = data_port & ontology_queries.is_shape_targeting_data(ontology, s)
        model_port = model_port & ontology_queries.is_shape_targeting_model(ontology,s)"""
    
    return not model_port,model_port

def inject_value(dataset:Dataset, value:Literal):
    
    raw_value = value.toPython()

    label = dataset.label[0].fragment if len(dataset.label) > 0 else '' #TODO allow multilabel problems
    
    if isinstance(raw_value,str):
        injections= [("$$LABEL$$", label ),
                    ('$$LABEL_CATEGORICAL$$', label),
                    ('$$NUMERIC_COLUMNS$$', f'{dataset.numeric_columns}'),
                    ('$$NUMERIC_AND_TARGET_COLUMNS$$',f'{dataset.numeric_columns + dataset.targets}'),
                    ('$$CATEGORICAL_COLUMNS$$',f'{dataset.categorical_columns}'),
                    ('$$PATH$$',f'{dataset.path}'),
                    ('$$DATA_RAW_FORMAT$$',f'{dataset.format}'),
                    ]
        
        for expression, newvalue in injections:
            raw_value = raw_value.replace(expression, newvalue)
    

    return raw_value

def condition_satisfied(condition:Literal, feature_types:Set):
    if condition is None:
        return True
    condition = condition.toPython()
    return condition == ""\
        or (condition == '$$INTEGER_COLUMN$$' and int not in feature_types) \
        or (condition == '$$STRING_COLUMN$$' and str not in feature_types) \
        or (condition == '$$FLOAT_COLUMN$$' and float not in feature_types)

def get_workflow_parameters(ontology:Graph, dataset:Dataset, implementation: URIRef, component:URIRef):
    parameters = ontology_queries.get_implementation_parameters(ontology, implementation)
    component_overriden_parameters = ontology_queries.get_component_overridden_parameters(ontology, component)
    parameters.update(component_overriden_parameters)


    parameters = {
        key: inject_value(dataset, value)
        for key, (value, order, condition) in parameters.items()
        if condition_satisfied(condition, dataset.feature_types)
    }
    return parameters



def get_most_suitable_predecessor(ontology:Graph, input_port:Tuple[Set[URIRef],Tuple[bool,bool]], candidates: List[Tuple[URIRef,List[URIRef],Tuple[bool,bool]]]): #TODO create candidate class
    """Get the most plausible component to connect to input_port. 
    This is infered based on the input shapes of each port candidate port and the target type.
    The returned candidate is ideally the one that contain all the shapes of the input port. 
    If ideal option is not found, it returns the one with more shapes in common.
    If no candidate share any shape with input_port, it returns a candidate with the same target
    (data or model) as input_port, starting at the end of the list.

    It is expected that candiates list is ordered based on ascending step order.
    """
    
    best_score = -1 #if shapes don't match, at least select a data/model candidate port that matches the input
    best_candidate = cb.NONE
    input_shapes, (input_targets_data, input_targets_model), input_component = input_port

    for port, shapes, (port_targets_data, port_targets_model), component  in reversed(candidates): #it is more likely to connect to the immediately precedent step
        #print(port, shapes, port_targets_data, port_tarets_model)
        
        if (port_targets_data and input_targets_data):
            #print(input_component, component, list(ontology.subjects(tb.hasApplier, input_component)))
            if component not in list(ontology.subjects(tb.hasApplier, input_component)):
                return port
        
        if(port_targets_model and input_targets_model): #do not consider a viable candidate if port_targets differ 
            return port
            # intersection = input_shapes & set(shapes)
            # print("intersection", intersection)

            # if len(intersection) == len(input_shapes):
            #     return port # Best possible match
            
            # if len(intersection) > best_score:
            #     best_candidate = port
            #     best_score = len(intersection)

    return best_candidate

def add_step(workflow_graph: Graph, workflow:URIRef, task_name: str, step_order:int, step_component: URIRef, 
             input_specs: List[URIRef], output_specs: List[URIRef], parameters:Dict[URIRef,Tuple[URIRef, URIRef, URIRef]], last_steps:List[URIRef], 
             step_columns: List[URIRef], step_columns_to_ignore: List[URIRef]) -> URIRef:
    
    triplets = []
    step = ab.term(task_name)
    triplets.append((workflow, tb.hasStep, step, workflow_graph))
    triplets.append((step, RDF.type, tb.Step, workflow_graph))
    triplets.append((step, tb.runs, step_component, workflow_graph))
    triplets.append((step, tb.has_position, Literal(step_order), workflow_graph))

    for column in step_columns:
        triplets.append((step, tb.over_column, column, workflow_graph))

    for column in step_columns_to_ignore:
        triplets.append((step, tb.ignores_column, column, workflow_graph))

    for i, (port, spec) in enumerate(input_specs):
        in_node = BNode()
        triplets.append((in_node, RDF.type, tb.Data, workflow_graph))
        triplets.append((in_node, tb.has_data, port, workflow_graph))
        triplets.append((in_node, tb.has_spec, spec, workflow_graph))
        triplets.append((in_node, tb.has_position, Literal(i), workflow_graph))
        triplets.append((step, tb.hasInput, in_node, workflow_graph))

    for o, (port, spec) in enumerate(output_specs):
        out_node = BNode()
        triplets.append((out_node, RDF.type, tb.Data, workflow_graph))
        triplets.append((out_node, tb.has_data, port, workflow_graph))
        triplets.append((out_node, tb.has_spec, spec, workflow_graph))
        triplets.append((out_node, tb.has_position, Literal(o), workflow_graph))
        triplets.append((step, tb.hasOutput, out_node, workflow_graph))

    for param, value in parameters.items():
        parameterSpec = ab.term(f'{param.fragment}_{step.fragment}_specification')
        triplets.append((parameterSpec, RDF.type, tb.ParameterSpecification, workflow_graph))
        triplets.append((param, tb.specifiedBy, parameterSpec, workflow_graph))
        triplets.append((parameterSpec, tb.hasValue, Literal(value), workflow_graph))
        triplets.append((step, tb.usesParameter, param, workflow_graph))

    for previous in last_steps:
        triplets.append((previous, tb.followedBy, step, workflow_graph))

    workflow_graph.addN(triplets)
    return step

step_cache = {}
model_shapes = set()
def build_workflow(ontology: Graph, workflow_graph:Graph, dataset: Dataset, max_imp_level:int, workflow_name:str, logical_plan:List[Tuple[URIRef,List[URIRef]]], transformer_columns = {}, run_transformations = False):
    prev_output_ports = {URIRef(c.split('--')[-1]) : [] for (c, follows) in logical_plan}
    prev_steps = {URIRef(c.split('--')[-1]) : [] for (c, follows) in logical_plan}

    workflow_uri = ab.term(workflow_name)
    workflow_graph.add((workflow_uri, RDF.type, tb.Workflow))

    compatibility = set(ontology_queries.get_engines(ontology))
    target_cols = set(dataset.targets)

    
    for step_order, (step_component, follows) in enumerate(logical_plan):

        step_data = step_cache.get(step_component)
        if step_data is None:
            component_uri = URIRef(step_component.split('--')[-1])
            #intent_parameters = get_intent_parameters()
            step_columns = transformer_columns.get(step_component, dataset.columns)
            step_columns = set([URIRef(c) for c in step_columns])

            step_columns_to_ignore = target_cols - step_columns #Columns to ignore are target columns, except if they are explicitly considered as a column to transform for this component
            
            step_implementation = ontology_queries.get_component_implementation(ontology, component_uri)
            step_name = f'{workflow_name}-step_{step_order}_{step_implementation.fragment.replace("-", "_")}'

            step_parameters = get_workflow_parameters(ontology, dataset, step_implementation, component_uri)

            input_specs  = ontology_queries.get_implementation_input_specs(ontology, step_implementation, max_imp_level) 
            output_specs = ontology_queries.get_implementation_output_specs(ontology, step_implementation, max_imp_level)

            step_cache[step_component] = (component_uri, step_implementation, input_specs, output_specs, step_columns, step_columns_to_ignore, step_parameters)

        else:
            component_uri, step_implementation, input_specs, output_specs, step_columns, step_columns_to_ignore, step_parameters = step_data



        step_name = f'{workflow_name}-step_{step_order}_{step_implementation.fragment.replace("-", "_")}'

        inputs = []
        prev_out_step_ports = prev_output_ports.get(component_uri, [])



        for spec, shapes in input_specs:
            if len(shapes) > 1 or cb.UnsatisfiableShape not in shapes: #ignore port if unsatisfiable
                input_target = get_port_target_type(shapes)
                input_port = get_most_suitable_predecessor(ontology,(set(shapes),input_target, component_uri), prev_out_step_ports)

                assert input_port != cb.NONE, f"{step_component}, {spec}\n{logical_plan}"
                inputs.append((input_port,spec))
        

        outputs = []
        output_ports = []
        for i, (spec, shapes) in enumerate(output_specs):

            if step_order == 0: #TODO it would be better to specify it as a special shape that denotes orignal dataset
                output_i = dataset.dataset
            else:
                output_i = ab[f'{step_name}-output_{i}']

            outputs.append((output_i,spec))
            output_ports.append((output_i, shapes, get_port_target_type(shapes),component_uri))

        step_uri = add_step(workflow_graph,workflow_uri,step_name, step_order, component_uri, inputs, outputs, step_parameters, prev_steps[component_uri], step_columns, step_columns_to_ignore)

        
        for f in follows:
            f_uri = URIRef(f.split('--')[-1])
            prev_output_ports[f_uri].extend(output_ports)
            prev_steps[f_uri].append(step_uri)

        if run_transformations:
            component_transformations = ontology_queries.get_component_transformations(ontology, component_uri)
            run_component_transformation(ontology, dataset, component_transformations, inputs, outputs, step_parameters)

        engine_compatibility = ontology_queries.get_implementation_engine_compatibility(ontology, step_implementation) #TODO: Check translation condition
        #print("engine compatibility for", step_implementation, engine_compatibility)
        compatibility = compatibility & engine_compatibility


    for engine in compatibility:
        workflow_graph.add((workflow_uri, tb.compatibleWith, engine)) 
    
    return workflow_graph, workflow_uri


def generate_workflows(ontology:Graph, intent_graph:Graph, data_graph:Graph, logical_plans:Dict[str,Dict[URIRef,List[URIRef]]], run_transformations=False):
    workflows = {}
    
    global step_cache 
    step_cache = {} #clear cache

    global model_shapes
    model_shapes = set(ontology.subjects(RDF.type, tb.ModelTag))

    intent_uri = intent_queries.get_intent_iri(intent_graph)
    dataset_uri = data_queries.get_dataset_uri(data_graph)
    
    max_imp_level = intent_queries.get_max_importance_level(intent_graph, intent_uri)
    dataset = Dataset(data_graph, dataset_uri)

    complete_intent = dataset.data_node_graph+intent_graph


    for i, (name, (plan, cols)) in enumerate(tqdm(logical_plans.items(),desc='Workflows built', position=0, leave=False)):
        workflow_graph = get_graph_xp()
        workflow_graph += complete_intent
        workflow_name = f'workflow_{i}_{intent_uri.fragment}_{uuid.uuid4()}'.replace('-', '_')
        workflow_graph, workflow_uri = build_workflow(ontology, workflow_graph, dataset, max_imp_level, workflow_name, plan, cols, run_transformations) #TODO fix transformations
        
        workflow_graph.add((workflow_uri, tb.generatedFor, intent_uri))
        workflow_graph.add((intent_uri, RDF.type, tb.Intent))
        
        workflows[name] = workflow_graph
        dataset.clear_node_graph()



    #t2 = time.time()
    #print("Temps total:", t2-t)

    return workflows


        


