import math
from tqdm import tqdm
from rdflib import Graph, URIRef, Literal

import os
import sys
root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

from common import *

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
    

def unpack_expression(ontology:Graph,alg_expr:URIRef):
    term1 = next(ontology.objects(alg_expr,tb.hasTerm1,unique=True),None)
    term2 = next(ontology.objects(alg_expr,tb.hasTerm2,unique=True),None)
    operation = next(ontology.objects(alg_expr,tb.hasOperation,unique=True),None)
    return term1, term2, operation

def is_parameter(ontology:Graph, uri:URIRef):
    query = f'''
    PREFIX tb: <{tb}>
    ASK {{
        {uri.n3()} a tb:Parameter .
        ?impl tb:hasParameter {uri.n3()} .
    }} 
    '''
    return ontology.query(query).askAnswer


def is_expression(ontology:Graph, uri:URIRef):
    query = f'''
    PREFIX tb: <{tb}>
    ASK {{
        {uri.n3()} a tb:AlgebraicExpression .
    }}
    '''
    return ontology.query(query).askAnswer

def compute_algebraic_expression(ontology: Graph, expression: URIRef, step_parameters:URIRef):
    term1, term2, operation = unpack_expression(ontology,expression)

    #print("Computing expression:", term1, term2, operation)

    assert not term1 is None and not operation is None
    operation = URIRef(operation).fragment
    assert (term2 is None and operation in ['COPY', 'SQRT']) or not term2 is None


    def compute_term_value(term):
        print("term",term,type(term))
        if isinstance(term,Literal):
            print("tipus",term.datatype)
            value = term.toPython()
        elif term == cb.NONE or term is None:
            value = None
        elif is_parameter(ontology, term):
            if term in step_parameters.keys():
                print("param one",step_parameters[term], step_parameters[term].datatype, type(step_parameters[term]))
                value = step_parameters[term].toPython()
            else:
                tqdm.write(str(term) +" not present in step parameters. Using default value")
                value= None
        elif is_expression(ontology, term):
            value = compute_algebraic_expression(ontology, term, step_parameters)
        else:
            raise Exception("Invalid term type: "+type+" for term: "+term)
        print("term final",term,value,type(value))
        return value
    
    value_1 = compute_term_value(term1)
    #print("Value 1:", value_1)
    value_2 = compute_term_value(term2)
    #print("Value 2:", value_2)

    result = calculate(value_1, value_2, operation)
    #print("Result:",result)

    if type(result) == float and result.is_integer():
        return int(result) #Always returns the result as integer when possible
    return result