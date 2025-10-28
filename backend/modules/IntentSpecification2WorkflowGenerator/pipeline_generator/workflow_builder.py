from ast import Set
from typing import Dict, List, Tuple
import uuid
from rdflib import Graph, URIRef
from graph_queries import ontology_queries, intent_queries, data_queries
from common import *


class Dataset:
    def __init__(self, data_graph: Graph, dataset:URIRef):
        self.data_graph = data_graph
        self.dataset = dataset
    
    def get_label(self):
        if self.label is None:
            self.label = data_queries.get_datset_label_name(self.data_graph, self.dataset)
        return self.label
    
    def get_numeric_columns(self):
        if self.numeric_columns is None:
            self.numerc_columns = data_queries.get_dataset_numeric_columns(self.data_graph, self.dataset)
        return self.numerc_columns
    
    def get_categorical_columns(self):
        if self.categorical_columns is None:
            self.categorical_columns = data_queries.get_dataset_categorical_columns(self.data_graph, self.dataset)
        return self.categorical_columns
    
    def get_target(self):
        if self.target is None:
            self.target = data_queries.get_dataset_target_column(self.data_graph, self.dataset)
        return self.target
    
    def get_format(self):
        if self.format is None:
            self.format = data_queries.get_dataset_format(self.data_graph, self.dataset)
        return self.format
    
    def get_path(self):
        if self.path is None:
            self.path = data_queries.get_dataset_path(self.data_graph, self.dataset)
        return self.path
    
    def get_feature_types(self):
        if self.feat_types is None:
            self.feat_types = data_queries.get_dataset_feature_types(self.data_graph, self.dataset)
        return self.feat_types
    

def inject_value(dataset:Dataset, value:str, intent_graph: Graph = None):

    injections= [("$$LABEL$$", dataset.get_label()),
                 ('$$LABEL_CATEGORICAL$$', dataset.get_label()),
                 ('$$NUMERIC_COLUMNS$$', f'{dataset.get_numeric_columns()}'),
                 ('$$NUMERIC_AND_TARGET_COLUMNS$$',f'{dataset.get_numeric_columns().append(dataset.get_target())}'),
                 ('$$CATEGORICAL_COLUMNS$$',f'{dataset.get_categorical_columns()}'),
                 ('$$PATH$$',f'{dataset.get_path()}'),
                 ('$$DATA_RAW_FORMAT$$',f'{dataset.get_format()}'),
                 ]
    
    for expression, newvalue in injections:
        value = value.replace(expression, newvalue)

    return value

def condition_satisfied(condition:str, feature_types:Set):
    return (condition == '$$INTEGER_COLUMN$$' and int not in feature_types) \
        or (condition == '$$STRING_COLUMN$$' and str not in feature_types) \
        or (condition == '$$FLOAT_COLUMN$$' and float not in feature_types)

def get_workflow_parameters(ontology:Graph, dataset:Dataset, implementation: URIRef, component:URIRef):
    parameters = ontology_queries.get_implementation_parameters(ontology, implementation)
    component_overriden_parameters = ontology_queries.get_component_overridden_parameters(ontology, component)
    parameters.update(component_overriden_parameters)


    for key, (value, order, condition) in parameters.items():
        if condition_satisfied(condition, dataset.get_feature_types()):
            parameters[key] = inject_value(value)
        else:
            parameters.drop(key)
    
    return parameters
            

# Try to guess the component connected to the input port with input_specs.
# It compares the input specs of the input port with the output specs of each previous component directly connected to the current step.
def get_most_suitable_predecessor(input_specs:Set[URIRef], candidates: Dict[URIRef, List[URIRef]]):
    best_score = 0
    best_candidate = None

    for component, specs in candidates.items():
        intersection = input_specs & set(specs)

        if len(intersection) == len(input_specs):
            return component # Best possible match
        
        if len(intersection) > best_score:
            best_candidate = component
            best_score = len(intersection)

    return best_candidate

def add_step(workflow_graph: Graph, workflow:URIRef, task_name: str, step_order:int, step_component: URIRef, 
             input_specs: List[URIRef], output_specs: List[URIRef], parameters:Dict[URIRef,Tuple[URIRef, URIRef, URIRef]], last_steps:List[URIRef]) -> URIRef:
    step = ab.term(task_name)
    workflow_graph.add((workflow, tb.hasStep, step))
    workflow_graph.add((step, RDF.type, tb.Step))
    workflow_graph.add((step, tb.runs, step_component))
    workflow_graph.add((step, tb.has_position, Literal(step_order)))
    for i, input in enumerate(input_specs):
        in_node = BNode()
        workflow_graph.add((in_node, RDF.type, tb.Data))
        workflow_graph.add((in_node, tb.has_data, input))
        #graph.add((in_node, tb.has_spec, input_specs[i][0]))
        workflow_graph.add((in_node, tb.has_position, Literal(i)))
        workflow_graph.add((step, tb.hasInput, in_node))

    
    for o, output in enumerate(output_specs):
        out_node = BNode()
        workflow_graph.add((out_node, RDF.type, tb.Data))
        workflow_graph.add((out_node, tb.has_data, output))
        #graph.add((out_node, tb.has_spec, output_specs[o][0]))
        workflow_graph.add((out_node, tb.has_position, Literal(o)))
        workflow_graph.add((step, tb.hasOutput, out_node))

    for param, (value, order, condition) in parameters.items():
        parameterSpec = ab.term[f'{param.fragment}_{step.fragment}_specification']
        workflow_graph.add((parameterSpec, RDF.type, tb.ParameterSpecification))
        workflow_graph.add((param, tb.specifiedBy, parameterSpec))
        workflow_graph.add((parameterSpec, tb.hasValue, Literal(value)))
        workflow_graph.add((step, tb.usesParameter, param))



    for previous in last_steps:
        workflow_graph.add((previous, tb.followedBy, step))
    return step

def build_workflow(ontology: Graph, intent_graph: Graph, intent_iri:URIRef, data_graph: Graph, dataset_uri: URIRef, logical_plan:dict):
    prev_output_specs = {}
    prev_steps = {c : [] for c in logical_plan.keys()}
    max_imp_level = intent_queries.get_max_importance_level(intent_graph, intent_iri)
    dataset = Dataset(data_graph, dataset_uri)

    workflow_name = f'workflow_{intent_iri.fragment}'.replace('-', '_')
    workflow_graph = get_graph_xp()
    workflow_uri = ab.term(workflow_name)
    workflow_graph.add((workflow_uri, RDF.type, tb.Workflow))
    

    for step_order, step_component, follows in enumerate(logical_plan.items):
        #intent_parameters = get_intent_parameters()
        
        step_implementation = ontology_queries.get_component_implementation(ontology, step_component)
        step_name = f'{workflow_name}-step_{step_order}_{step_implementation.fragment.replace("-", "_")}'

        step_parameters = get_workflow_parameters(ontology, dataset, step_implementation, step_component)

        input_specs = ontology_queries.get_implementation_input_specs(ontology, step_implementation, max_imp_level) 
        output_specs = ontology_queries.get_implementation_output_specs(ontology, step_implementation, max_imp_level)

        inputs = [None for i in input_specs]

        prev_out_step_specs = prev_output_specs.get(step_component, [])
        for i, inp in enumerate(input_specs):
            inputs[i] = get_most_suitable_predecessor(set(inp), prev_out_step_specs)

        outputs = [ab[f'{step_name}-output_{i}'] for i in range(len(output_specs))]

        step_uri = add_step(workflow_graph,workflow_uri,step_name, step_order, step_component, inputs, outputs, step_parameters, prev_steps[step_component])

        for f in follows:
            prev_output_specs[f].append(output_specs)
            prev_steps[f].append(step_uri)


    workflow_graph.add((workflow_uri, tb.generatedFor, intent_iri))
    workflow_graph.add((intent_iri, RDF.type, tb.Intent))


        


