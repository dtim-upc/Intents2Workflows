from rdflib import Graph, URIRef, Literal
from typing import Dict, List, Tuple
import math
from tqdm import tqdm

import os
import sys
root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

from common import *
from .algebraic_expression_computation import compute_algebraic_expression
from graph_queries.ontology_queries import get_text_parameter_base_parameter, get_implementation_parameters, is_factor, \
    translate_factor_level, get_algebraic_expression, get_parameter_key

def literal_to_raw_datatype(value):
    if isinstance(value, Literal):
        return value.toPython()
    elif value == cb.NONE:
        return None
    return value

def translate_text_params(ontology:Graph, implementation:URIRef, step_parameters: Dict[URIRef,Literal]):
    python_params = {}
    text_params = get_implementation_parameters(ontology,implementation, tb.TextParameter)

    for param, (default_value, order, condition) in text_params.items():
        base_param = get_text_parameter_base_parameter(ontology, param)
        if base_param in step_parameters.keys():
            if is_factor(ontology, param):
                value = translate_factor_level(ontology, base_param, step_parameters[base_param],param)
            else:
                value = step_parameters[base_param]
        else:
            value = default_value

        value = literal_to_raw_datatype(value)
        key = get_parameter_key(ontology,param).toPython()
        
        python_params[param] = (key,value)
    return python_params


def translate_numeric_params(ontology:Graph, implementation:URIRef, step_parameters: Dict[URIRef,Literal]):
    python_params = {}
    numeric_params =  get_implementation_parameters(ontology,implementation, tb.NumericParameter)


    for param, (default_value, order, condition) in numeric_params.items():
        alg_expression = get_algebraic_expression(ontology, param)
        value = compute_algebraic_expression(ontology, alg_expression, step_parameters)
 
        if value is None:
            value = default_value

        value = literal_to_raw_datatype(value)

        key = get_parameter_key(ontology,param)
        python_params[param] = (key,value)
    return python_params

def get_engine_specific_params(ontology:Graph, implementation:URIRef):
    params = {}
    specific_params = get_implementation_parameters(ontology,implementation,tb.EngineSpecificParameter)

    for param, (default_value, order, condition) in specific_params.items():

        value = literal_to_raw_datatype(default_value)

        key = get_parameter_key(ontology,param)
        params[param] = (key,value)
    return params

def translate_parameters(ontology:Graph, step_parameters:URIRef, engine_implementation:URIRef):
    text_params = translate_text_params(ontology, engine_implementation, step_parameters)
    numeric_params: Dict = translate_numeric_params(ontology, engine_implementation, step_parameters)
    specific_params = get_engine_specific_params(ontology,engine_implementation)
    
    return text_params | numeric_params | specific_params