from typing import List

import os 
import sys
from .engine_parameter import EngineParameter, EngineNumericParameter, EngineTextParameter, EngineFactorParameter, EngineSpecificParameter
from .implementation import Implementation
from .expression import AlgebraicExpression
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from common import *

class EngineImplementation():
    def __init__(self, name: str, engine: URIRef, baseImplementation: Implementation, parameters: List[EngineParameter], translation_condition: AlgebraicExpression = None, namespace: Namespace = cb) -> None:
        self.parameters = parameters
        self.baseImplementation = baseImplementation
        self.name = name
        self.engine = engine

        self.url_name = f'{self.engine.fragment}-implementation-{self.name.replace(" ", "_").replace("-", "_").lower()}'
        self.namespace = namespace
        self.uri_ref = self.namespace[self.url_name]

        self.translation_condition = translation_condition

        for parameter in self.parameters:
            parameter.uri_ref = self.namespace[f'{self.url_name}-{parameter.url_name}']
 
    def add_to_graph(self, g: Graph):
        g.add((self.uri_ref, RDF.type, tb.EngineImplementation))

        g.add((self.uri_ref, tb.has_engine, self.engine))

        g.add((self.uri_ref, tb.term('name'), Literal(self.name)))


        if self.translation_condition is not None:
            print(self.translation_condition)
            condtion_uri = self.translation_condition.add_to_graph(g)
            g.add((self.uri_ref, tb.has_translation_condition, condtion_uri))
 
        # Parameters
        for parameter in self.parameters:
            if isinstance(parameter, EngineParameter):
                if isinstance(parameter, EngineTextParameter):
                    #assert parameter.base_parameter.datatype == parameter.datatype, f"Datatype missmatch in {parameter.label} -> base: {parameter.base_parameter.datatype}, engine: {parameter.datatype}"

                    g.add((parameter.uri_ref, RDF.type, tb.TextParameter))
                    g.add((parameter.uri_ref, tb.hasBaseParameter, parameter.base_parameter.uri_ref))
                
                    if isinstance(parameter, EngineFactorParameter):
        
                        for key, value in parameter.levels_dict.items():
                            assert value in parameter.base_parameter.levels, f"Level {value} not in base parameter levels {parameter.base_parameter.levels}"
                            level_uri = parameter.uri_ref + '-'+ key
                            base_level_uri = parameter.base_parameter.uri_ref + '-' + value
                            g.add((level_uri, RDF.type, tb.FactorLevel))
                            g.add((level_uri, tb.hasValue, Literal(key)))
                            g.add((parameter.uri_ref, tb.hasLevel, level_uri))
                            g.add((level_uri, tb.equivalentTo, base_level_uri))
                        g.add((parameter.uri_ref, RDF.type, tb.FactorParameter))
                        g.add((parameter.uri_ref, tb.hasBaseParameter, parameter.base_parameter.uri_ref))
                
                elif isinstance(parameter, EngineNumericParameter):
                    expression_uri = parameter.expression.add_to_graph(g) 
                    g.add((parameter.uri_ref, RDF.type, tb.DerivedParameter))
                    g.add((parameter.uri_ref, tb.derivedFrom, expression_uri))
                    g.add((parameter.uri_ref, RDF.type, tb.NumericParameter))
                
                elif isinstance(parameter, EngineSpecificParameter):
                    g.add((parameter.uri_ref, RDF.type, tb.EngineSpecificParameter))
                    

                default_value = parameter.default_value
                if default_value is None:
                    g.add((parameter.uri_ref, tb.has_default_value, cb.NONE))
                else:
                    g.add((parameter.uri_ref, tb.has_default_value, Literal(default_value)))

                g.add((parameter.uri_ref, tb.key, Literal(parameter.label)))
                g.add((parameter.uri_ref, tb.has_datatype, parameter.datatype))
                #g.add((parameter.uri_ref, tb.has_engine, parameter.engine))

                g.add((self.uri_ref, tb.hasParameter, parameter.uri_ref))
                g.add((parameter.uri_ref, RDF.type, tb.EngineParameter)) #TODO propper subclassing

        # Base implementation
        g.add((self.uri_ref, tb.hasBaseImplementation, self.baseImplementation.uri_ref))
        g.add((self.baseImplementation.uri_ref, tb.compatibleWith, self.engine)) 

        return self.uri_ref
    
    def add_counterpart_relationship(self, cbox):
        #TODO remove this
        pass

