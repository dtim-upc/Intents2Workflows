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


def literal_to_raw_datatype(value):
    if isinstance(value, Literal):
        return value.toPython()
    elif value == cb.NONE:
        return None
    return value

def translate_text_params(ontology:Graph, implementation:URIRef, step_parameters: Dict[URIRef,Literal], engine:str):
    python_params = {}
    text_params = queries.get_engine_text_params(ontology,implementation,engine=engine)
    target = None

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


def calculate(term1, term2, operation):
    if term1 is None or (term2 is None and operation not in ['COPY', "SQRT"]):
        return None

    if operation == "SUM":
        return term1 + term2
    elif operation == "SUB":
        return term1 - term2
    elif operation == "MUL":
        return term1 * term2
    elif operation == "DIV":
        return term1 / term2
    elif operation == "POW":
        return term1 ^ term2 
    elif operation == "SQRT":
        return math.sqrt(term1)
    elif operation == "EQ":
        return term1 == term2
    elif operation == "NEQ":
        return term1 != term2
    elif operation == 'COPY':
        return term1
    else:
        raise Exception("Invalid operation: "+operation)


def compute_algebraic_expression(ontology: Graph, expression: URIRef, step_parameters:URIRef):
    term1, term2, operation = queries.unpack_expression(ontology,expression)

    assert not term1 is None and not operation is None
    operation = URIRef(operation).fragment
    assert (term2 is None and operation in ['COPY', 'SQRT']) or not term2 is None


    def compute_term_value(term):
        t = term if not term is None else "res"
        #tqdm.write("termvalue de "+t)
        if isinstance(term,Literal):
            tqdm.write("termvalue de "+t)
            value = term.toPython()
        elif term == cb.NONE or term is None:
            value = None
        elif queries.is_parameter(ontology, term):
            tqdm.write("termvalue de "+t)
            if term in step_parameters.keys():
                value = step_parameters[term].toPython()
            else:
                tqdm.write("Term "+term+" not present in step parameters. Using default value")
                value= None
        elif queries.isExpression(ontology, term):
            tqdm.write("termvalue algebraic de "+t)
            value = compute_algebraic_expression(ontology, term, step_parameters)
        else:
            raise Exception("Invalid term type: "+type+" for term: "+term)
        
        return value
    
    value_1 = compute_term_value(term1)
    value_2 = compute_term_value(term2)

    return calculate(value_1, value_2, operation)


def translate_numeric_params(ontology:Graph, implementation:URIRef, step_parameters: Dict[URIRef,Literal], engine:str):
    python_params = {}
    numeric_params = queries.get_engine_numeric_params(ontology,implementation,engine=engine)

    for param in numeric_params:
        alg_expression = queries.get_algebraic_expression(ontology, param)
        value = compute_algebraic_expression(ontology, alg_expression, step_parameters)

        if value is None:
            value = queries.get_default_value(ontology, param)

        value = literal_to_raw_datatype(value)

        key = next(ontology.objects(param, tb.key, unique=True))
        python_params[key] = value
    return python_params

def get_engine_specific_params(ontology:Graph, implementation:URIRef, engine:str):
    params = {}
    specific_params = queries.get_engine_specific_params(ontology,implementation,engine=engine)

    for param in specific_params:
        value = queries.get_default_value(ontology, param)
        value = literal_to_raw_datatype(value)

        key = next(ontology.objects(param, tb.key, unique=True))
        params[key] = value
    return params

def get_step_parameters_agnostic(ontology: Graph, workflow_graph: Graph, step: URIRef) -> List[Tuple[str, str, str, URIRef]]:

    parameters = list(workflow_graph.objects(step, tb.usesParameter, True))
 
    step_parameters = {}

    for param in parameters:
        spec = next(workflow_graph.objects(param, tb.specifiedBy, True))
        value = next(workflow_graph.objects(spec, tb.hasValue, True))
        step_parameters[param] = value

    return step_parameters

def translate_parameters(ontology:Graph, workflow_graph: Graph, step:URIRef, implementation:URIRef, engine:str):
    step_parameters = get_step_parameters_agnostic(ontology, workflow_graph, step)

    text_params = translate_text_params(ontology, implementation, step_parameters,engine)
    numeric_params: Dict = translate_numeric_params(ontology,  implementation, step_parameters,engine)
    specific_params = get_engine_specific_params(ontology,implementation,engine=engine)
    return text_params | numeric_params | specific_params