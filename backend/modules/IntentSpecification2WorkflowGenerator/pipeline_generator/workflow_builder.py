from typing import Dict, List, Tuple, Set
import uuid
from rdflib import Graph, URIRef
from .graph_queries import ontology_queries, intent_queries, data_queries
from common import *


class Dataset:
    def __init__(self, data_graph: Graph, dataset:URIRef):
        self.data_graph = data_graph
        self.dataset = dataset
        self._label = None
        self._numeric_columns = None
        self._categorical_columns = None
        self._target = None
        self._format = None
        self._path = None
        self._feat_types = None
    
    @property
    def label(self):
        if self._label is None:
            self._label = data_queries.get_datset_label_name(self.data_graph, self.dataset)
        return self._label
    
    @property
    def numeric_columns(self):
        if self._numeric_columns is None:
            self._numerc_columns = data_queries.get_dataset_numeric_columns(self.data_graph, self.dataset)
        return self._numerc_columns
    
    @property
    def categorical_columns(self):
        if self._categorical_columns is None:
            self._categorical_columns = data_queries.get_dataset_categorical_columns(self.data_graph, self.dataset)
        return self._categorical_columns
    
    @property
    def target(self):
        if self._target is None:
            self._target = data_queries.get_dataset_target_column(self.data_graph, self.dataset)
        return self._target
    
    @property
    def format(self):
        if self._format is None:
            self._format = data_queries.get_dataset_format(self.data_graph, self.dataset)
        return self._format
    
    @property
    def path(self):
        if self._path is None:
            self._path = data_queries.get_dataset_path(self.data_graph, self.dataset)
        return self._path
    
    @property
    def feature_types(self):
        if self._feat_types is None:
            self._feat_types = data_queries.get_dataset_feature_types(self.data_graph, self.dataset)
        return self._feat_types
    

def inject_value(dataset:Dataset, value:str):

    injections= [("$$LABEL$$", dataset.label),
                 ('$$LABEL_CATEGORICAL$$', dataset.label),
                 ('$$NUMERIC_COLUMNS$$', f'{dataset.numeric_columns}'),
                 ('$$NUMERIC_AND_TARGET_COLUMNS$$',f'{dataset.numeric_columns.append(dataset.target)}'),
                 ('$$CATEGORICAL_COLUMNS$$',f'{dataset.categorical_columns}'),
                 ('$$PATH$$',f'{dataset.path}'),
                 ('$$DATA_RAW_FORMAT$$',f'{dataset.format}'),
                 ]
    
    for expression, newvalue in injections:
        value = value.replace(expression, newvalue)

    return value

def condition_satisfied(condition:str, feature_types:Set):
    return condition is None \
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
            

# Try to guess the component connected to the input port with input_specs.
# It compares the input specs of the input port with the output specs of each previous component directly connected to the current step.
def get_most_suitable_predecessor(input_shapes:Set[URIRef], candidates: List[Tuple[URIRef,List[URIRef]]]):
    best_score = 0
    best_candidate = cb.NONE
    print("Candidates", candidates)
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

    for param, value in parameters.items():
        parameterSpec = ab.term(f'{param.fragment}_{step.fragment}_specification')
        workflow_graph.add((parameterSpec, RDF.type, tb.ParameterSpecification))
        workflow_graph.add((param, tb.specifiedBy, parameterSpec))
        workflow_graph.add((parameterSpec, tb.hasValue, Literal(value)))
        workflow_graph.add((step, tb.usesParameter, param))

    for previous in last_steps:
        workflow_graph.add((previous, tb.followedBy, step))
    return step


def build_workflow(ontology: Graph, dataset: Dataset, max_imp_level:int, workflow_name:str, logical_plan:List[Tuple[URIRef,List[URIRef]]]):
    prev_output_ports = {URIRef(c) : [] for (c, follows) in logical_plan}
    prev_steps = {URIRef(c) : [] for (c, follows) in logical_plan}
    print(prev_steps, prev_output_ports)

    workflow_graph = get_graph_xp()
    workflow_uri = ab.term(workflow_name)
    workflow_graph.add((workflow_uri, RDF.type, tb.Workflow))
    

    for step_order, (step_component, follows) in enumerate(logical_plan):
        #intent_parameters = get_intent_parameters()
        step_component = URIRef(step_component)
        print("STEP:", step_component)
        
        step_implementation = ontology_queries.get_component_implementation(ontology, step_component)
        step_name = f'{workflow_name}-step_{step_order}_{step_implementation.fragment.replace("-", "_")}'

        step_parameters = get_workflow_parameters(ontology, dataset, step_implementation, step_component)

        input_specs  = ontology_queries.get_implementation_input_specs(ontology, step_implementation, max_imp_level) 
        output_specs = ontology_queries.get_implementation_output_specs(ontology, step_implementation, max_imp_level)
        print(output_specs)

        inputs = []
        prev_out_step_ports = prev_output_ports.get(step_component, [])
        for i, (sepc, shapes) in enumerate(input_specs):
            print(shapes)
            inputs.append(get_most_suitable_predecessor(set(shapes), prev_out_step_ports))


        outputs = []
        output_ports = []
        for i, (spec, shapes) in enumerate(output_specs):
            output_i = ab[f'{step_name}-output_{i}']
            outputs.append(output_i)
            output_ports.append((output_i, shapes))


        step_uri = add_step(workflow_graph,workflow_uri,step_name, step_order, step_component, inputs, outputs, step_parameters, prev_steps[step_component])

        for f in follows:
            prev_output_ports[URIRef(f)].extend(output_ports)
            prev_steps[URIRef(f)].append(step_uri)

    return workflow_graph, workflow_uri


def generate_workflows(ontology:Graph, intent_graph:Graph, data_graph:Graph, logical_plans:Dict[str,Dict[URIRef,List[URIRef]]]):
    workflows = {}

    intent_uri = intent_queries.get_intent_iri(intent_graph)
    dataset_uri = data_queries.get_dataset_uri(data_graph)
    
    max_imp_level = intent_queries.get_max_importance_level(intent_graph, intent_uri)
    dataset = Dataset(data_graph, dataset_uri)

    for i, (name, plan) in enumerate(logical_plans.items()):
        workflow_name = f'workflow_{i}_{intent_uri.fragment}_{uuid.uuid4()}'.replace('-', '_')
        workflow_graph, workflow_uri = build_workflow(ontology, dataset, max_imp_level, workflow_name, plan)
        
        workflow_graph.add((workflow_uri, tb.generatedFor, intent_uri))
        workflow_graph.add((intent_uri, RDF.type, tb.Intent))
        workflows[name] = workflow_graph

    return workflows


        


