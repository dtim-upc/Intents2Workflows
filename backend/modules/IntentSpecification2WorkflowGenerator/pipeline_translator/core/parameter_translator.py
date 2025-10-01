from rdflib import Graph, URIRef, Literal
from typing import Dict, List, Tuple
import math
from tqdm import tqdm

import os
import sys
root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

from common import *
from . import translator_graph_queries as queries
from .algebraic_expression_computation import compute_algebraic_expression


def literal_to_raw_datatype(value):
    if isinstance(value, Literal):
        return value.toPython()
    elif value == cb.NONE:
        return None
    return value

def translate_text_params(ontology:Graph, implementation:URIRef, step_parameters: Dict[URIRef,Literal]):
    python_params = {}
    text_params = queries.get_text_params(ontology,implementation)

    for param in text_params:
        base_param = queries.get_base_param(ontology, param)
        if base_param in step_parameters.keys():
            if queries.is_factor(ontology, param):
                value = queries.translate_factor_level(ontology, base_param, step_parameters[base_param],param)
            else:
                value = step_parameters[base_param]
        else:
            value = queries.get_default_value(ontology, param)

        value = literal_to_raw_datatype(value)
        key = next(ontology.objects(param, tb.key, unique=True))
        
        print(key, value)
        python_params[key] = value
    return python_params


def translate_numeric_params(ontology:Graph, implementation:URIRef, step_parameters: Dict[URIRef,Literal]):
    python_params = {}
    numeric_params = queries.get_numeric_params(ontology,implementation)

    for param in numeric_params:
        alg_expression = queries.get_algebraic_expression(ontology, param)
        value = compute_algebraic_expression(ontology, alg_expression, step_parameters)
 
        if value is None:
            value = queries.get_default_value(ontology, param)

        value = literal_to_raw_datatype(value)

        key = next(ontology.objects(param, tb.key, unique=True))
        python_params[key] = value
    return python_params

def get_engine_specific_params(ontology:Graph, implementation:URIRef):
    params = {}
    specific_params = queries.get_engine_specific_params(ontology,implementation)

    for param in specific_params:
        value = queries.get_default_value(ontology, param)
        value = literal_to_raw_datatype(value)

        key = next(ontology.objects(param, tb.key, unique=True))
        params[key] = value
    return params

def translate_parameters(ontology:Graph, step_parameters:URIRef, engine_implementation:URIRef):
    text_params = translate_text_params(ontology, engine_implementation, step_parameters)
    numeric_params: Dict = translate_numeric_params(ontology, engine_implementation, step_parameters)
    specific_params = get_engine_specific_params(ontology,engine_implementation)
    
    return text_params | numeric_params | specific_params