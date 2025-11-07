import os
from typing import Dict, List, Tuple
import sys
from rdflib import Literal

root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

from common import *
from .algebraic_expression_computation import compute_algebraic_expression
from graph_queries.ontology_queries import get_engine_implementations, get_translation_condition

def get_ontology() -> Graph:
    cwd = os.getcwd()
    os.chdir('..')
    ontology = common.get_ontology_graph()
    os.chdir(cwd)
    return ontology

def load_workflow(path: str) -> Graph:
    graph = get_graph_xp()
    graph.parse(path, format='turtle')
    return graph


def get_implementation_engine_conditional(ontology: Graph, base_implementation: URIRef, engine:URIRef, parameters):

    implementations = get_engine_implementations(ontology, base_implementation, engine)
    print("Implementacions",implementations)

    for implementation in implementations:
        cond = get_translation_condition(ontology, implementation)
        
        if cond is None or compute_algebraic_expression(ontology, cond, parameters):
            return implementation #returns the first compatible engine implementation
        
    print(f"ERROR: No translation condition matched for {base_implementation} in {engine} engine.")
    return None
        #print(f"WARNING: More than one engine implementations found for {base_implementation} in {engine} engine. Only one of them (chosen randomly) will be used")
    

