from typing import List

import os 
import sys
from .engine_parameter import EngineParameter, EngineNumericParameter, EngineTextParameter, EngineFactorParameter
from .implementation import Implementation
from .parameter import FactorParameter
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from common import *

class EngineImplementation(Implementation):
    def __init__(self, name: str, engine: str, baseImplementation: Implementation, parameters: List[EngineParameter], namespace: Namespace = cb) -> None:
        self.parameters = parameters
        self.baseImplementation = baseImplementation
        self.name = name
        self.engine = engine

        self.url_name = f'{self.engine}-implementation-{self.name.replace(" ", "_").replace("-", "_").lower()}'
        self.namespace = namespace
        self.uri_ref = self.namespace[self.url_name]

        for parameter in self.parameters:
            parameter.uri_ref = self.namespace[f'{self.url_name}-{parameter.url_name}']

    def add_to_graph(self, g: Graph):
        g.add((self.uri_ref, RDF.type, tb.EngineImplementation))

        g.add((self.uri_ref, tb.engine, Literal(self.engine)))

        g.add((self.uri_ref, tb.term('name'), Literal(self.name)))

        # Parameters
        for parameter in self.parameters:
            if isinstance(parameter, EngineParameter):
                #assert parameter.base_parameter.datatype == parameter.datatype, "Datatype missmatch -> Converters must be implemented"

                if isinstance(parameter, EngineTextParameter):

                    g.add((parameter.uri_ref, RDF.type, tb.TextParameter))
                    g.add((parameter.uri_ref, tb.hasBaseParameter, parameter.base_parameter.uri_ref))
                
                    if isinstance(parameter, EngineFactorParameter):
                        assert isinstance(parameter.base_parameter, FactorParameter) and len(parameter.base_parameter.levels) == len(parameter.levels)
                        #Now enumerations mapping are done assuming as 1 by 1 relation between both enummerations.

                        for i, level in enumerate(parameter.levels):
                            level_uri = parameter.uri_ref + '-'+ level
                            base_level_uri = parameter.base_parameter.uri_ref + '-' + parameter.base_parameter.levels[i]
                            g.add((level_uri, RDF.type, tb.FactorLevel))
                            g.add((level_uri, tb.hasValue, Literal(level)))
                            g.add((parameter.uri_ref, tb.hasLevel, level_uri))
                            g.add((level_uri, tb.equivalentTo, base_level_uri))
                        g.add((parameter.uri_ref, RDF.type, tb.FactorParameter))
                        g.add((parameter.uri_ref, tb.hasBaseParameter, parameter.base_parameter.uri_ref))
                
                elif isinstance(parameter, EngineNumericParameter):
                    expression_uri = parameter.expression.add_to_graph(g)
                    g.add((parameter.uri_ref, RDF.type, tb.DerivedParameter))
                    g.add((parameter.uri_ref, tb.derivedFrom, expression_uri))
                    g.add((parameter.uri_ref, RDF.type, tb.NumericParameter))

                default_value = parameter.default_value
                if default_value is None:
                    g.add((parameter.uri_ref, tb.has_default_value, cb.NONE))
                else:
                    g.add((parameter.uri_ref, tb.has_default_value, Literal(default_value)))

                g.add((parameter.uri_ref, tb.key, Literal(parameter.label)))

                g.add((self.uri_ref, tb.hasParameter, parameter.uri_ref))

        # Base implementation
        g.add((self.uri_ref, tb.hasBaseImplementation, self.baseImplementation.uri_ref))

        return self.uri_ref
    
    def add_counterpart_relationship(self, cbox):
        #TODO remove this
        pass

