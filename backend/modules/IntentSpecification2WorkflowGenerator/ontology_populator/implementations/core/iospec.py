from typing import List
from rdflib import Graph, URIRef
from common import *

class IOSpecTag:
    def __init__(self, shape:URIRef, importance_level = 0):
        self.shape = shape
        self.imp_level = importance_level

    def add_to_graph(self, g:Graph):
        dataspectag_node = BNode()
        g.add((dataspectag_node, RDF.type, tb.DataSpecTag))
        g.add((dataspectag_node, tb.hasDatatag, self.shape))
        g.add((dataspectag_node, tb.hasImportanceLevel, Literal(self.imp_level)))

        return dataspectag_node

class IOSpec:
    def __init__(self, io_tags:List[IOSpecTag], type:str, namespace = cb):
        self.specs = io_tags
        self.type = type
        self.url_name = f"IOSpec-{hash(str(io_tags))}-{type}"
        self.namespace = namespace
        self.uri = self.namespace[self.url_name]
    
    def add_to_graph(self, g: Graph):
        g.add((self.uri, RDF.type, tb.DataSpec)) 

        for tag in self.specs:
                spectag = tag.add_to_graph(g)
                g.add((self.uri, tb.hasSpecTag, spectag))
         
        return self.uri
 
class InputIOSpec(IOSpec):
     def __init__(self, io_tags:List[IOSpecTag], namespace = cb):
          super().__init__(io_tags, 'Input', namespace)

class OutputIOSpec(IOSpec):
     def __init__(self, io_tags:List[IOSpecTag], namespace = cb):
          super().__init__(io_tags, 'Output', namespace)