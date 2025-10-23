from rdflib import Graph, URIRef
from typing import List
from tqdm import tqdm

from .graph_queries import intent_queries, ontology_queries, shape_queries
from common import *


def get_algorithms_from_task_constrained(ontology:Graph, shape_graph:Graph, task: URIRef) -> URIRef:
    algs_unconstr = ontology_queries.get_algorithms_from_task(ontology, task)
    return shape_queries.reinforce_constraint(shape_graph, ontology,  ab.AlgorithmConstraint, algs_unconstr)


def get_potential_implementations_constrained(ontology:Graph, shape_graph:Graph, algorithm: URIRef, exclude_appliers=True) -> \
        List[URIRef]:
    pot_impl_unconstr = ontology_queries.get_potential_implementations(ontology, algorithm, exclude_appliers)
    return shape_queries.reinforce_constraint(shape_graph, ontology, ab.ImplementationConstraint, pot_impl_unconstr)

def get_algorithms_and_implementations_to_solve_task(ontology: Graph, shape_graph, intent_graph: Graph,log: bool = False):
    
    intent_iri = intent_queries.get_intent_iri(intent_graph=intent_graph)
    dataset, task, algorithm = intent_queries.get_intent_dataset_task(intent_graph, intent_iri) 
    
    if log:
        tqdm.write(f'Intent: {intent_iri.fragment}')
        tqdm.write(f'Dataset: {dataset.fragment}')
        tqdm.write(f'Task: {task.fragment}')
        tqdm.write(f'Algorithm: {algorithm.fragment if algorithm is not None else [algo.fragment for algo in get_algorithms_from_task_constrained(ontology, shape_graph,task)]}')
        tqdm.write('-------------------------------------------------')

    #option_explorer.get_best_options(intent_graph, ontology)

    algs = algorithm if not algorithm is None else get_algorithms_from_task_constrained(ontology,shape_graph,task)
    
    pot_impls = []
    for al in algs:
        pot_impls.extend(get_potential_implementations_constrained(ontology, shape_graph, al))
    
    return algs, pot_impls