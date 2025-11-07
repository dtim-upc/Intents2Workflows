from typing import Dict, List, Literal as Lit, Tuple
from rdflib import Graph, URIRef, Literal
from common import *


def get_workflow_steps(workflow_graph: Graph) -> List[URIRef]:
    steps = list(workflow_graph.subjects(RDF.type, tb.Step))

    connections = list(workflow_graph.subject_objects(tb.followedBy))
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

def get_step_component(workflow_graph: Graph, step: URIRef) -> Tuple[URIRef, URIRef]:
    component = next(workflow_graph.objects(step, tb.runs, True))
    return component

def get_step_io_specs(workflow_graph:Graph, step:URIRef, type:str):
    query = f"""PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                SELECT ?pos ?spec
                WHERE {{ 
                    {step.n3()} tb:has{type} ?inp .
                    ?inp tb:has_spec ?spec ;
                        tb:has_position ?pos .       
                }} 
                ORDER BY ?pos
            """
    results = workflow_graph.query(query).bindings
    return [result['spec'] for result in results]

def get_step_input_specs(workflow_graph:Graph, step:URIRef):
    return get_step_io_specs(workflow_graph, step, 'Input')

def get_step_output_specs(workflow_graph:Graph, step:URIRef):
    return get_step_io_specs(workflow_graph, step, 'Output')

def get_step_io_data(workflow_graph:Graph, step:URIRef, type:str):
    query = f"""PREFIX tb: <https://extremexp.eu/ontology/tbox#>
            SELECT ?pos ?data 
            WHERE {{ 
                {step.n3()} tb:has{type} ?inp .
                ?inp 
                    tb:has_data ?data ;
                    tb:has_position ?pos .    
            }} 
            ORDER BY ?pos"""
    result = workflow_graph.query(query).bindings
    return [ inp['data'] for inp in result ]


def get_step_input_data(workflow_graph:Graph, step:URIRef):
    return get_step_io_data(workflow_graph, step, 'Input')

def get_step_output_data(workflow_graph:Graph, step:URIRef):
    return get_step_io_data(workflow_graph, step, 'Output')

def get_workflow_intent_number(workflow_graph: Graph) -> int:
    return int(next(workflow_graph.subjects(RDF.type, tb.Workflow, True)).fragment.split('_')[1])


def get_workflow_connections(workflow_graph: Graph) -> List[Tuple[URIRef, URIRef, URIRef, URIRef]]:
    query = f'''
    PREFIX tb: <{tb}>
    SELECT ?source ?destination ?sourcePort ?destinationPort
    WHERE {{
        ?source a tb:Step ;
                tb:followedBy ?destination ;
                tb:hasOutput ?output .
        ?output tb:has_position ?sourcePort ;
                tb:has_data ?link .
        ?destination a tb:Step ;
                    tb:hasInput ?input .
        ?input tb:has_position ?destinationPort ;
                tb:has_data ?link .
    }}
    '''
    results = workflow_graph.query(query).bindings
    # print(f'RESULTS: {results}')
    return [(r['source'], r['destination'], r['sourcePort'], r['destinationPort']) for r in results]


def get_step_parameters_agnostic(workflow_graph: Graph, step: URIRef) -> Dict[URIRef,Literal]:

    parameters = list(workflow_graph.objects(step, tb.usesParameter, True))
 
    step_parameters = {}

    for param in parameters:
        spec = next(workflow_graph.objects(param, tb.specifiedBy, True))
        value = next(workflow_graph.objects(spec, tb.hasValue, True))
        step_parameters[param] = value

    return step_parameters