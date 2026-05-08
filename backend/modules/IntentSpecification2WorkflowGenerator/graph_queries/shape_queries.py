from collections import defaultdict

from rdflib import Graph, URIRef
from pyshacl import validate
from typing import List

from common import SH, dmop, RDF



from collections import defaultdict
from rdflib.namespace import SH

  

def get_nodes_that_NOT_satisfy_shape(data_graph: Graph, shacl_graph: Graph, shape: URIRef, focus_nodes: List[URIRef]) -> set:

    conforms, results_graph, report = validate(
        data_graph=data_graph,
        shacl_graph=shacl_graph,
        validate_shapes= [shape],
        focus=focus_nodes
    )

    #if not conforms:
    #    print(report)

    fails = set()

    for r in results_graph.subjects(RDF.type, SH.ValidationResult):
        node = results_graph.value(r, SH.focusNode)
        fails.add(node)

    return fails

def get_nodes_that_satisfy_shape(data_graph: Graph, shacl_graph: Graph, shape: URIRef, focus_nodes: List[URIRef]):

    failed_ndoes = get_nodes_that_NOT_satisfy_shape(data_graph, shacl_graph, shape, focus_nodes)

    all_nodes = set(focus_nodes)

    return all_nodes - failed_ndoes
            

def reinforce_constraint(shape_graph:Graph, ontology:Graph, constraint:URIRef, unconstrained_nodes:List[URIRef]):

    results = get_nodes_that_satisfy_shape(ontology, shape_graph, shape=constraint, focus_nodes=unconstrained_nodes)
    
    return results


def iscolumnar(ontology:Graph, shape):
    return (shape, SH.targetClass, dmop.Column) in ontology