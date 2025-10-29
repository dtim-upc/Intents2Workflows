import zipfile
import sys
import os
from typing import Dict

from rdflib.term import Node, URIRef

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common import *
from pipeline_generator.graph_queries import intent_queries, ontology_queries
from typing import List, Tuple
from pipeline_generator.graph_queries.ontology_queries import get_implementation_io_specs, get_constraint_by_name, get_engines
from pipeline_generator import abstract_planner as abstractPlannerModule, pipeline_generator, workflow_builder

def get_custom_ontology(path):
    graph = get_graph_xp()
    ontologies = [
        r'ontologies/tbox.ttl',
        r'ontologies/cbox.ttl',
        r'ontologies/abox.ttl',
        path
    ]
    for o in ontologies:
        graph.parse(o, format="turtle")

    DeductiveClosure(OWLRL_Semantics).expand(graph)
    return graph

def get_custom_ontology_only_problems():
    graph = get_graph_xp()
    ontologies = [
        r'ontologies/tbox.ttl',
        r'ontologies/cbox.ttl',
        r'ontologies/abox.ttl',
    ]
    for o in ontologies:
        graph.parse(o, format="turtle")

    DeductiveClosure(OWLRL_Semantics).expand(graph)
    return graph

def get_constraint(ontology: Graph, name: str):
    return get_constraint_by_name(ontology,name)


def connect_algorithms(ontology, shape_graph, algos_list: List[URIRef]):

    linked_impls = {}
    partition = False

    for i in range(1,len(algos_list)):
        connections = [algos_list[i]]
        
        if partition:
            connections.append(algos_list[i]+"-Train")
            linked_impls[algos_list[i]+"-Train"] = [algos_list[i+1]]
            partition = False
        linked_impls[algos_list[i-1]] = connections

        if algos_list[i] == cb.Partitioning:
            partition = True

        

    linked_impls[algos_list[-1]] = []

    return linked_impls



def abstract_planner(ontology: Graph, shape_graph: Graph, intent: Graph) -> Tuple[
    Dict[Node, Dict[Node, List[Node]]], Dict[Node, List[Node]]]:

    intent_iri = intent_queries.get_intent_iri(intent)
    task = intent_queries.get_intent_task(intent, intent_iri)
    algs, impls = abstractPlannerModule.get_algorithms_and_implementations_to_solve_task(ontology, shape_graph, intent, log=True)
    algs_shapes = {}
    alg_plans = {alg: [] for alg in algs}
    available_algs = [] # to make sure abstract plans are only made for algorithms with at least one available implementation
    for impl in impls:
        alg = next(ontology.objects(impl, tb.implements)), 
        (impl, RDF.type, tb.Implementation) in ontology and (tb.ApplierImplementation not in ontology.objects(impl, RDF.type))

        input_specs = get_implementation_io_specs(ontology, impl, "Input")
        if len(input_specs) > 0:
            algs_shapes[alg[0]] = input_specs[0] #assuming data shapes is on input 0 
        else:
            algs_shapes[alg[0]] = []
       
        alg_plans[alg[0]].append(impl)
        available_algs.append(alg[0])
    
    plans = {}

    for alg in available_algs:
        print(alg)
        if len(algs_shapes[alg]) <= 0:
            plans[alg] = connect_algorithms(ontology, shape_graph, [alg])
        elif cb.TrainTabularDatasetShape in algs_shapes[alg] or cb.TrainTensorDatasetShape in algs_shapes[alg]:
            plans[alg] = connect_algorithms(ontology, shape_graph,[cb.DataLoading, cb.Partitioning, alg, cb.DataStoring])
        elif task == cb.Clustering:
            plans[alg] = connect_algorithms(ontology, shape_graph,[cb.DataLoading, alg, cb.DataStoring])
        else:
            plans[alg] = connect_algorithms(ontology, shape_graph, [cb.DataLoading, alg])
    return plans, alg_plans
    

def getCompatibility(workflow_graph: Graph, engine:URIRef):
    workflow_id = next(workflow_graph.subjects(RDF.type, tb.Workflow, unique=True),None)
    compatible = (workflow_id,tb.compatibleWith,engine) in workflow_graph
    return compatible

def compress(folder: str, destination: str) -> None:
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                archive_path = os.path.relpath(file_path, folder)
                zipf.write(file_path, arcname=os.path.join(os.path.basename(folder), archive_path))
