from typing import Tuple
from rdflib import Graph, URIRef
from common import *


def get_intent_iri(intent_graph: Graph) -> URIRef:
    intent_iri_query = f"""
PREFIX tb: <{tb}>
SELECT ?iri
WHERE {{
    ?iri a tb:Intent .
}}
"""
    result = intent_graph.query(intent_iri_query).bindings
    assert len(result) == 1
    return result[0]['iri']


def get_intent_dataset_task(intent_graph: Graph, intent_iri: URIRef) -> Tuple[URIRef, URIRef, URIRef]:
    dataset_task_query = f"""
    PREFIX tb: <{tb}>
    SELECT ?dataset ?task ?algorithm
    WHERE {{
        {intent_iri.n3()} a tb:Intent .
        {intent_iri.n3()} tb:overData ?dataset .
        ?task tb:tackles {intent_iri.n3()} .
        OPTIONAL {{{intent_iri.n3()} tb:specifies ?algorithm}}
    }}
"""
    result = intent_graph.query(dataset_task_query).bindings[0]
    return result['dataset'], result['task'], result.get('algorithm', None)

def get_intent_task(intent_graph: Graph, intent_iri: URIRef) -> URIRef:
    dataset_task_query = f"""
    PREFIX tb: <{tb}>
    SELECT ?dataset ?task ?algorithm
    WHERE {{
        {intent_iri.n3()} a tb:Intent .
        ?task tb:tackles {intent_iri.n3()} .
    }}
"""
    result = intent_graph.query(dataset_task_query).bindings[0]
    return result['task']

def get_intent_dataset_format(intent_graph: Graph, intent_iri: URIRef) -> Tuple[URIRef, URIRef, URIRef]:
    dataset_task_query = f"""
    PREFIX tb: <{tb}>
    SELECT ?format
    WHERE {{
        {intent_iri.n3()} a tb:Intent .
        {intent_iri.n3()} tb:overData ?dataset .
        ?dataset dmop:fileFormat ?format .
    }}
"""
    result = intent_graph.query(dataset_task_query).bindings[0]
    return result['format']


def get_intent_parameters(intent_graph: Graph):
    intent_parameters_query = f"""
    PREFIX tb:<{tb}>
    SELECT ?exp_param ?param_val
    WHERE{{
        ?param_val tb:forParameter ?exp_param .
    }}
"""
    result = intent_graph.query(intent_parameters_query).bindings
    return {param['exp_param']:param['param_val'] for param in result}


def get_component_threshold(intent_graph: Graph, intent_iri:URIRef):
    return float(next(intent_graph.objects(intent_iri, tb.has_component_threshold), 1.0))

def get_max_importance_level(intent_graph: Graph, intent_iri:URIRef):
    return int(next(intent_graph.objects(intent_iri, tb.has_complexity), 3))

