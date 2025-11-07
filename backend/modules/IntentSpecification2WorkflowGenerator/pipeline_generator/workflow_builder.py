from typing import Dict, List, Tuple, Set
import uuid
from rdflib import Graph, URIRef, Literal, BNode
from graph_queries import ontology_queries, intent_queries, data_queries
from .utils.dataset import Dataset
from .utils.transformation_engine import run_component_transformation
from common import *
import time
 

def inject_value(dataset:Dataset, value:Literal):
    
    raw_value = value.toPython()
    
    if isinstance(raw_value,str):
        injections= [("$$LABEL$$", dataset.label),
                    ('$$LABEL_CATEGORICAL$$', dataset.label),
                    ('$$NUMERIC_COLUMNS$$', f'{dataset.numeric_columns}'),
                    ('$$NUMERIC_AND_TARGET_COLUMNS$$',f'{dataset.numeric_columns.append(dataset.target)}'),
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
    print("PARAMS",parameters)
    return parameters
            

# Try to guess the component connected to the input port with input_specs.
# It compares the input specs of the input port with the output specs of each previous component directly connected to the current step.
def get_most_suitable_predecessor(input_shapes:Set[URIRef], candidates: List[Tuple[URIRef,List[URIRef]]]):
    best_score = 0
    best_candidate = cb.NONE
    for port, shapes in candidates:       
        intersection = input_shapes & set(shapes)

        if len(intersection) == len(input_shapes):
            return port # Best possible match
        
        if len(intersection) > best_score:
            best_candidate = port
            best_score = len(intersection)

    return best_candidate

def add_step(workflow_graph: Graph, workflow:URIRef, task_name: str, step_order:int, step_component: URIRef, 
             input_specs: List[URIRef], output_specs: List[URIRef], parameters:Dict[URIRef,Tuple[URIRef, URIRef, URIRef]], last_steps:List[URIRef]) -> URIRef:
    step = ab.term(task_name)
    workflow_graph.add((workflow, tb.hasStep, step))
    workflow_graph.add((step, RDF.type, tb.Step))
    workflow_graph.add((step, tb.runs, step_component))
    workflow_graph.add((step, tb.has_position, Literal(step_order)))

    for i, (port, spec) in enumerate(input_specs):
        in_node = BNode()
        workflow_graph.add((in_node, RDF.type, tb.Data))
        workflow_graph.add((in_node, tb.has_data, port))
        workflow_graph.add((in_node, tb.has_spec, spec))
        workflow_graph.add((in_node, tb.has_position, Literal(i)))
        workflow_graph.add((step, tb.hasInput, in_node))

    for o, (port, spec) in enumerate(output_specs):
        out_node = BNode()
        workflow_graph.add((out_node, RDF.type, tb.Data))
        workflow_graph.add((out_node, tb.has_data, port))
        workflow_graph.add((out_node, tb.has_spec, spec))
        workflow_graph.add((out_node, tb.has_position, Literal(o)))
        workflow_graph.add((step, tb.hasOutput, out_node))

    for param, value in parameters.items():
        parameterSpec = ab.term(f'{param.fragment}_{step.fragment}_specification')
        workflow_graph.add((parameterSpec, RDF.type, tb.ParameterSpecification))
        workflow_graph.add((param, tb.specifiedBy, parameterSpec))
        workflow_graph.add((parameterSpec, tb.hasValue, Literal(value)))
        workflow_graph.add((step, tb.usesParameter, param))

    for previous in last_steps:
        workflow_graph.add((previous, tb.followedBy, step))
    return step


def build_workflow(ontology: Graph, dataset: Dataset, max_imp_level:int, workflow_name:str, logical_plan:List[Tuple[URIRef,List[URIRef]]], run_transformations = False):
    prev_output_ports = {URIRef(c) : [] for (c, follows) in logical_plan}
    prev_steps = {URIRef(c) : [] for (c, follows) in logical_plan}

    workflow_graph = get_graph_xp()
    workflow_uri = ab.term(workflow_name)
    workflow_graph.add((workflow_uri, RDF.type, tb.Workflow))

    compatibility = set(ontology_queries.get_engines(ontology))
    

    for step_order, (step_component, follows) in enumerate(logical_plan):
        #intent_parameters = get_intent_parameters()
        step_component = URIRef(step_component)
        
        step_implementation = ontology_queries.get_component_implementation(ontology, step_component)
        step_name = f'{workflow_name}-step_{step_order}_{step_implementation.fragment.replace("-", "_")}'

        step_parameters = get_workflow_parameters(ontology, dataset, step_implementation, step_component)

        input_specs  = ontology_queries.get_implementation_input_specs(ontology, step_implementation, max_imp_level) 
        output_specs = ontology_queries.get_implementation_output_specs(ontology, step_implementation, max_imp_level)

        inputs = []
        prev_out_step_ports = prev_output_ports.get(step_component, [])


        for i, (spec, shapes) in enumerate(input_specs):
            if cb.UnsatisfiableShape not in shapes: #ignore port if unsatisfiable
                input_port = get_most_suitable_predecessor(set(shapes), prev_out_step_ports)
                inputs.append((input_port,spec))
  
        outputs = []
        output_ports = []
        for i, (spec, shapes) in enumerate(output_specs):

            if step_order == 0: #TODO it would be better to specify it as a special shape that denotes orignal dataset
                output_i = dataset.dataset
            else:
                output_i = ab[f'{step_name}-output_{i}']

            outputs.append((output_i,spec))
            output_ports.append((output_i, shapes))


        step_uri = add_step(workflow_graph,workflow_uri,step_name, step_order, step_component, inputs, outputs, step_parameters, prev_steps[step_component])

        for f in follows:
            prev_output_ports[URIRef(f)].extend(output_ports)
            prev_steps[URIRef(f)].append(step_uri)

        if run_transformations:
            component_transformations = ontology_queries.get_component_transformations(ontology, step_component)
            run_component_transformation(ontology, dataset, component_transformations, inputs, outputs, step_parameters)

        engine_compatibility = ontology_queries.get_implementation_engine_compatibility(ontology, step_implementation) #TODO: Check translation condition
        compatibility = compatibility & engine_compatibility

    for engine in compatibility:
        workflow_graph.add((workflow_uri, tb.compatibleWith, engine))  

    return workflow_graph, workflow_uri


def generate_workflows(ontology:Graph, intent_graph:Graph, data_graph:Graph, logical_plans:Dict[str,Dict[URIRef,List[URIRef]]], run_transformations=False):
    t = time.time()
    workflows = {}

    intent_uri = intent_queries.get_intent_iri(intent_graph)
    dataset_uri = data_queries.get_dataset_uri(data_graph)
    
    max_imp_level = intent_queries.get_max_importance_level(intent_graph, intent_uri)
    dataset = Dataset(data_graph, dataset_uri)


    for i, (name, plan) in enumerate(logical_plans.items()):
        workflow_name = f'workflow_{i}_{intent_uri.fragment}_{uuid.uuid4()}'.replace('-', '_')
        workflow_graph, workflow_uri = build_workflow(ontology, dataset, max_imp_level, workflow_name, plan,run_transformations) #TODO fix transformations
        
        workflow_graph.add((workflow_uri, tb.generatedFor, intent_uri))
        workflow_graph.add((intent_uri, RDF.type, tb.Intent))
        workflow_graph += intent_graph
        workflow_graph += dataset.data_node_graph
        workflows[name] = workflow_graph
        dataset.clear_node_graph()

    t2 = time.time()
    print("Temps total:", t2-t)

    return workflows


        


