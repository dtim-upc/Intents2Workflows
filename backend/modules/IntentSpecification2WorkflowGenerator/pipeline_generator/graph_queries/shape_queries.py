from rdflib import Graph, URIRef
from pyshacl import validate
from typing import List

def satisfies_shape(data_graph: Graph, shacl_graph: Graph, shape: URIRef, focus: URIRef) -> bool:
    conforms, g, report = validate(data_graph, shacl_graph=shacl_graph, validate_shapes=[shape], focus=focus)
    #if not conforms:
    #    tqdm.write(report)
    return conforms
        

def reinforce_constraint(shape_graph:Graph, ontology:Graph, node_shape:URIRef, unconstrained_nodes:List[URIRef]):
    constrained_nodes = []

    for node in unconstrained_nodes:
        if satisfies_shape(ontology, shape_graph, shape=node_shape, focus=node):
            constrained_nodes.append(node)
    
    return constrained_nodes