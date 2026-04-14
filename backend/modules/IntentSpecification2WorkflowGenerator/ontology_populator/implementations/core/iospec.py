from typing import List
from rdflib import Graph, URIRef, BNode, RDF, Literal, Namespace
from common import *

#tb = Namespace('https://extremexp.eu/ontology/tbox#')
#cb = Namespace('https://extremexp.eu/ontology/cbox#')



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

        if len(self.specs) == 1:
             id = self.specs[0].shape.fragment
        else:
             id = hash(str(io_tags))
        self.url_name = f"{type}Spec-{id}"
        self.namespace = namespace
        self.implementation = BNode()
    
    def add_to_graph(self, g: Graph, implementation=URIRef):
        self.uri = self.get_uri(implementation)
        #print("Adding", self.specs, "to graph for imp", implementation.fragment, self.uri.fragment)

        if (self.uri, RDF.type, tb.DataSpec) not in g:
            g.add((self.uri, RDF.type, tb.DataSpec)) 

            for tag in self.specs:
                    spectag = tag.add_to_graph(g)
                    g.add((self.uri, tb.hasSpecTag, spectag))
            
        return self.uri
    
    def get_uri(self, implementation):
         return self.namespace[f"{implementation.fragment}-{self.url_name}"]
    
    def __eq__ (self, other):
        if isinstance(other, IOSpec) and self.type == other.type:
            own_shapes = set(s.shape.fragment for s in self.specs)
            other_shapes = set(s.shape.fragment for s in other.specs)
            #print("Igualant",own_shapes, other_shapes)
            return own_shapes == other_shapes
        return False
    
    def __hash__ (self):
         return hash((self.type,frozenset([s.shape.fragment for s in self.specs])))

 
class InputIOSpec(IOSpec):
     def __init__(self, io_tags:List[IOSpecTag], namespace = cb):
          super().__init__(io_tags, 'Input', namespace)

class OutputIOSpec(IOSpec):
     def __init__(self, io_tags:List[IOSpecTag], namespace = cb):
          super().__init__(io_tags, 'Output', namespace)


# tags = [IOSpecTag(cb.zzoneshape), IOSpecTag(cb.othershape)]
# tags2 = [IOSpecTag(cb.othershape), IOSpecTag(cb.zzoneshape)]

# i1 = InputIOSpec(tags)
# i2 = InputIOSpec(tags2)

# print(i1==i2)
# print(hash(i1), hash(i2))