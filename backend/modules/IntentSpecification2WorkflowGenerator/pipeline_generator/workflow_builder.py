from ast import Set
from typing import Dict
from rdflib import Graph, URIRef
from graph_queries import ontology_queries, intent_queries


def get_workflow_parameters(ontology:Graph, implementation: URIRef, component:URIRef):
    parameters = ontology_queries.get_implementation_parameters(ontology, implementation)
    component_overriden_parameters = ontology_queries.get_component_overridden_parameters(ontology, component)
    parameters.update(component_overriden_parameters)

    for key, value in parameters.items():
        if not condition_satisfied():
            parameters.drop(key)
        
        parameters[key] = inject_value(value)






# Try to guess the component connected to the input port with input_specs.
# It compares the input specs of the input port with the output specs of each previous component directly connected to the current step.
def get_most_suitable_predecessor(input_specs:Set[URIRef], candidates: Dict[URIRef, URIRef]):
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

def build_workflow(ontology: Graph, intent_graph: Graph, intent_iri:URIRef, data_graph: Graph, logical_plan:dict):
    prev_output_specs = {}
    max_imp_level = intent_queries.get_max_importance_level(intent_graph, intent_iri)

    for step_component, follows in logical_plan.items:
        #intent_parameters = get_intent_parameters()
        step_implementation = ontology_queries.get_component_implementation(ontology, step_component)
       

        input_specs = ontology_queries.get_implementation_input_specs(ontology, step_implementation, max_imp_level) 
        output_specs = ontology_queries.get_implementation_output_specs(ontology, step_implementation, max_imp_level)

        inputs = [None for i in input_specs]
        outputs = [None for i in output_specs]

        prev_out_step_specs = prev_output_specs.get(step_component, [])

        for i, inp in enumerate(input_specs):
            inputs[i] = get_most_suitable_predecessor(set(inp), prev_out_step_specs)

        for f in follows:
            prev_output_specs[f].append(outputs)
        


