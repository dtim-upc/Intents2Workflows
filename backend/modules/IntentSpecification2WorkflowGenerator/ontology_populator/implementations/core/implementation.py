from typing import List, Union

import os 
import sys
from .parameter import Parameter, FactorParameter
from .iospec import InputIOSpec, OutputIOSpec
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from common import *


LiteralValue = Union[str, bool, int, float, None]


class Implementation:
    def __init__(self, name: str, algorithm: URIRef,
                 parameters: List[Parameter],
                 input: List[InputIOSpec] = None,
                 output: List[OutputIOSpec] = None,
                 implementation_type=tb.Implementation,
                 counterpart: 'Implementation' = None,
                 namespace: Namespace = cb,
                 ) -> None:
        super().__init__()
        self.name = name
        self.url_name = f'implementation-{self.name.replace(" ", "_").replace("-", "_").lower()}'
        self.namespace = namespace
        self.uri_ref = self.namespace[self.url_name]
        self.parameters = {param: param for param in parameters}
        self.algorithm = algorithm
        self.input = input or []
        self.output = output or []
        assert implementation_type in {tb.Implementation, tb.LearnerImplementation, tb.ApplierImplementation, tb.VisualizerImplementation}
        self.implementation_type = implementation_type
        self.counterpart = counterpart
        if self.counterpart is not None:
            assert implementation_type in {tb.LearnerImplementation, tb.ApplierImplementation, tb.VisualizerImplementation}
            if isinstance(self.counterpart, list):
                for c in self.counterpart:
                    print(c)
                    if c.counterpart is None:
                        c.counterpart = self
            elif self.counterpart.counterpart is None:
                self.counterpart.counterpart = self

        for parameter in self.parameters.values():
            parameter.uri_ref = self.namespace[f'{self.url_name}-{parameter.url_name}']

    def add_to_graph(self, g: Graph):

        # Base triples
        g.add((self.uri_ref, RDF.type, self.implementation_type))
        g.add((self.uri_ref, RDFS.label, Literal(self.name)))
        g.add((self.uri_ref, tb.implements, self.algorithm))
        #g.add((self.uri_ref, tb.engine, Literal('Simple')))


        # Input triples
        for i,input_tag in enumerate(self.input):  
            input_uri = input_tag.add_to_graph(g)
            g.add((self.uri_ref, tb.specifiesInput, input_uri))  
            g.add((input_uri, tb.has_position, Literal(i))) 

        # Output triples
        for i,output_tag in enumerate(self.output):
            output_uri = output_tag.add_to_graph(g)
            g.add((self.uri_ref, tb.specifiesOutput, output_uri))
            g.add((output_uri, tb.has_position, Literal(i))) 

        # Parameter triples
        for i, parameter in enumerate(self.parameters):
            g.add((parameter.uri_ref, RDF.type, tb.Parameter))
            g.add((parameter.uri_ref, RDFS.label, Literal(parameter.label)))
            g.add((parameter.uri_ref, tb.has_datatype, parameter.datatype))
            g.add((parameter.uri_ref, tb.has_position, Literal(i)))
            g.add((parameter.uri_ref, tb.has_condition, Literal(parameter.condition)))
            if not parameter.default_value is None:
                if isinstance(parameter.default_value, URIRef):
                    g.add((parameter.uri_ref, tb.has_defaultvalue, parameter.default_value))
                else:
                    g.add((parameter.uri_ref, tb.has_defaultvalue, Literal(parameter.default_value)))

            if isinstance(parameter, FactorParameter):
                print("BaseFactor detectat:",parameter)
                for level in parameter.levels:
                    level_uri = parameter.uri_ref + '-'+ level
                    g.add((level_uri, RDF.type, tb.FactorLevel))
                    g.add((level_uri, tb.hasValue, Literal(level)))
                    g.add((parameter.uri_ref, tb.hasLevel, level_uri))

            g.add((self.uri_ref, tb.hasParameter, parameter.uri_ref))
        return self.uri_ref

    def add_counterpart_relationship(self, g: Graph):
        if self.counterpart is None:
            return
        counters = self.counterpart if isinstance(self.counterpart, list) else [self.counterpart]
        for c in counters:
            counterpart_query = f'''
            PREFIX tb: <{tb}>
            SELECT ?self ?counterpart
            WHERE {{
                ?self a <{self.implementation_type}> ;
                    rdfs:label "{self.name}" .
                ?counterpart a <{c.implementation_type}> ;
                    rdfs:label "{c.name}" .
            }}
            '''
            result = g.query(counterpart_query).bindings
            assert len(result) == 1
            self_node = result[0][Variable('self')]
            relationship = tb.hasApplier if self.implementation_type == tb.LearnerImplementation else tb.hasLearner
            counterpart_node = result[0][Variable('counterpart')]
            g.add((self_node, relationship, counterpart_node))