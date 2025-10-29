from rdflib import Graph, URIRef, IdentifiedNode, BNode
from common import *


def copy_subgraph(source_graph: Graph, source_node: URIRef, destination_graph: Graph, destination_node: URIRef,
                  replace_nodes: bool = True) -> None:
    visited_nodes = set()
    nodes_to_visit = [source_node]
    mappings = {source_node: destination_node}

    while nodes_to_visit:
        current_node = nodes_to_visit.pop()
        visited_nodes.add(current_node)
        for predicate, object in source_graph.predicate_objects(current_node):
            if predicate == OWL.sameAs:
                continue
            if replace_nodes and isinstance(object, IdentifiedNode):
                if predicate == RDF.type or object in dmop:
                    mappings[object] = object
                else:
                    if object not in visited_nodes:
                        nodes_to_visit.append(object)
                    if object not in mappings:
                        mappings[object] = BNode()
                destination_graph.add((mappings[current_node], predicate, mappings[object]))
            else:
                destination_graph.add((mappings[current_node], predicate, object))