import os
from typing import List, Tuple
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import *
from pipeline_generator.graph_queries import get_implementation_input_specs


def get_implementation_task(ontology: Graph, implementation: URIRef):
    query = f""" PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                SELECT ?task
                WHERE {{ {implementation.n3()} tb:implements ?task .}} """
    print(query)
    
    results = ontology.query(query).bindings
    print(results)

    assert len(results) == 1

    return results[0]['task']


def load_workflow(path: str) -> Graph:
    graph = get_graph_xp()
    graph.parse(path, format='turtle')
    return graph


def get_workflow_steps(graph: Graph) -> List[URIRef]:
    steps = list(graph.subjects(RDF.type, tb.Step))

    connections = list(graph.subject_objects(tb.followedBy))
    disordered = True
    while disordered:
        disordered = False
        for source, target in connections:
            si = steps.index(source)
            ti = steps.index(target)
            if si > ti:
                disordered = True
                steps[si] = target
                steps[ti] = source
    return steps


def get_step_component_implementation(ontology: Graph, workflow_graph: Graph, step: URIRef) -> Tuple[URIRef, URIRef]:
    component = next(workflow_graph.objects(step, tb.runs, True))
    implementation = next(ontology.objects(component, tb.hasImplementation, True))
    return component, implementation

def get_number_of_output_ports(ontology: Graph, workflow_graph: Graph, step: URIRef) -> int:
    _, implementation = get_step_component_implementation(ontology, workflow_graph, step)
    return sum(1 for _ in ontology.objects(implementation, tb.specifiesOutput))

def get_step_parameters(ontology: Graph, workflow_graph: Graph, step: URIRef) -> List[Tuple[str, str, str, URIRef]]:
    # print(f'STEP: {step}')
    parameters = list(workflow_graph.objects(step, tb.usesParameter, True))
    # print(f'PARAMETERS: {len(parameters)}')
    param_specs = [next(workflow_graph.objects(param, tb.specifiedBy, True)) for param in parameters]
    # print(f'PARAM SPECS: {param_specs}')
    param_values = [next(workflow_graph.objects(ps, tb.hasValue, True)) for ps in param_specs]
    # print(f'VALUES: {param_values}')
    keys = [next(ontology.objects(p, tb.knime_key, True), None) for p in parameters]
    # print(f'KEYS: {len(keys)}')
    paths = [next(ontology.objects(p, tb.knime_path, True)).value for p in parameters]
    # print(f'PATHS: {paths}')
    types = [next(ontology.objects(p, tb.has_datatype, True)) for p in parameters]
    # print(f'TYPES: {types}')
    return list(zip(keys, param_values, paths, types))


def get_workflow_intent_name(workflow_graph: Graph) -> str:
    return next(workflow_graph.subjects(RDF.type, tb.Intent, True)).fragment


def get_workflow_intent_number(workflow_graph: Graph) -> int:
    return int(next(workflow_graph.subjects(RDF.type, tb.Workflow, True)).fragment.split('_')[1])