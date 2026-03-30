from typing import List, Literal, Tuple

from rdflib import Graph, Namespace, URIRef, RDF
from I2WG.common import cb, sh

class BaseShape:
    def __init__(self, name: str, type:Literal['columnar', 'dataset'], dependences:List[URIRef], 
                 transformations:List[Tuple[URIRef, URIRef]], namespace:Namespace = cb):
        self.name = name
        self.type = type
        self.dependences = dependences
        self.transformations = transformations
        self.namespace = namespace


class ConditionalShape:
    def __init__(self, base_shape: BaseShape, condition:URIRef, namespace:Namespace = cb):
        self.base_shape = base_shape
        self.condition = condition
        self.namespace = namespace

    def add_to_graph(self, g: Graph)-> None:
        
        shape_node = self.namespace[self.name]

        triples = []
        triples.append((shape_node, RDF.type, sh.PropertyShape))

        for pred, obj in self.shape:
            triples.append((shape_node, pred, obj))