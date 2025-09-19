from enum import Enum
from typing import List, Union, Optional

from common import *
from ontology_populator.implementations.core import Implementation, Parameter, BaseFactorParameter, BaseParameter
from ontology_populator.implementations.core.parameter import LiteralValue


class AlgebraicExpression:
    def __init__(self, operation: URIRef, term1: Union[Parameter, 'AlgebraicExpression', LiteralValue], term2:  Union[Parameter, 'AlgebraicExpression', LiteralValue] = None):
        self.operation = Literal(operation)
        self.term1 = term1
        self.term2 = term2

    def add_to_graph(self, g: Graph):

        def term_to_uri(term):

            if term is None:
                return cb.NONE
            elif isinstance(term, AlgebraicExpression):
                return term.add_to_graph(g)
            elif isinstance(term, Parameter) or isinstance(term, BaseParameter): #TODO fix parameter subclasses mess
                return term.uri_ref
            elif isinstance(term, LiteralValue):
                return Literal(term)
            else:
                print(term)
                raise Exception("invalid term type")

        expr = BNode()
        g.add((expr,RDF.type,tb.AlgebraicExpression))
        g.add((expr, tb.hasOperation, self.operation))
        
        term1_uri = term_to_uri(self.term1)
        g.add((expr,tb.hasTerm1, term1_uri))
        
        if not self.term2 is None:
            term2_uri = term_to_uri(self.term2)
            g.add((expr,tb.hasTerm2, term2_uri))
        
        return expr

#TODO derived from EngineParameter
class PythonParameter:

    def __init__(self, python_key: str, datatype: URIRef,  
                default_value: Union[URIRef, LiteralValue]) -> None:
       
        self.python_key = python_key
        self.datatype = datatype
        self.default_value = default_value
       
        self.url_name = self.python_key.replace(' ', '_').replace('-', '_').lower()

        self.uri_ref = None

class PythonNumericParameter(PythonParameter):
    def __init__(self, python_key: str, datatype: URIRef,
                expression: AlgebraicExpression, default_value: Union[URIRef, LiteralValue]) -> None:
        
        super().__init__(python_key, datatype, default_value)
    
        self.expression = expression


class PythonFactorParameter(PythonParameter):

    def __init__(self, python_key: str, levels: List[str], base_parameter: Parameter, 
                 default_value: Union[URIRef, LiteralValue]) -> None:
        super().__init__(python_key, XSD.enumeration,  default_value)
        self.base_parameter = base_parameter
        self.levels = levels

class PythonTextParameter(PythonParameter):
    def __init__(self, python_key: str, base_parameter: Parameter, 
                 default_value: Union[URIRef, LiteralValue]) -> None:
        super().__init__(python_key, XSD.string,  default_value)
        self.base_parameter = base_parameter


class PythonImplementation:

    def __init__(self, name: str, baseImplementation: Implementation, parameters: List[PythonParameter],
                 python_module, module_version, python_function, template, namespace: Namespace = cb) -> None:
        self.python_module = python_module
        self.python_module_version = module_version
        self.python_function = python_function
        self.template = template
        self.parameters = parameters
        self.baseImplementation = baseImplementation
        self.name = name

        self.url_name = f'python-implementation-{self.name.replace(" ", "_").replace("-", "_").lower()}'
        self.namespace = namespace
        self.uri_ref = self.namespace[self.url_name]

        for parameter in self.parameters:
            parameter.uri_ref = self.namespace[f'{self.url_name}-{parameter.url_name}']

    def add_to_graph(self, g: Graph):
        g.add((self.uri_ref, RDF.type, tb.EngineImplementation))

        g.add((self.uri_ref, tb.engine, Literal('Python')))

        g.add((self.uri_ref, tb.term('name'), Literal(self.name)))

        g.add((self.uri_ref, tb.term('python_module'), Literal(self.python_module)))
        g.add((self.uri_ref, tb.term('python_function'), Literal(self.python_function)))
        g.add((self.uri_ref, tb.term('python_version'), Literal(self.python_module_version)))
        g.add((self.uri_ref, tb.term('template'), Literal(self.template)))

        # Parameters
        for parameter in self.parameters:
            if isinstance(parameter, PythonParameter):
                #assert parameter.base_parameter.datatype == parameter.datatype, "Datatype missmatch -> Converters must be implemented"

                if isinstance(parameter, PythonFactorParameter):
                    assert isinstance(parameter.base_parameter, BaseFactorParameter) and len(parameter.base_parameter.levels) == len(parameter.levels)
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
                
                elif isinstance(parameter, PythonNumericParameter):
                    expression_uri = parameter.expression.add_to_graph(g)
                    g.add((parameter.uri_ref, RDF.type, tb.DerivedParameter))
                    g.add((parameter.uri_ref, tb.derivedFrom, expression_uri))
                    g.add((parameter.uri_ref, RDF.type, tb.NumericParameter))

                elif isinstance(parameter, PythonTextParameter):
                    g.add((parameter.uri_ref, RDF.type, tb.TextParameter))
                    g.add((parameter.uri_ref, tb.hasBaseParameter, parameter.base_parameter.uri_ref))


                
                g.add((parameter.uri_ref, tb.python_key, Literal(parameter.python_key)))
                g.add((parameter.uri_ref, tb.has_datatype, Literal(parameter.datatype)))

                default_value = parameter.default_value
                if default_value is None:
                    g.add((parameter.uri_ref, tb.has_default_value, cb.NONE))
                else:
                    g.add((parameter.uri_ref, tb.has_default_value, Literal(default_value)))

                #g.add((parameter.uri_ref, tb.has_default_value, default_value)) #TODO allow for null default values
                g.add((self.uri_ref, tb.hasParameter, parameter.uri_ref))

        # Base implementation
        g.add((self.uri_ref, tb.hasBaseImplementation, self.baseImplementation.uri_ref))

        return self.uri_ref
    
    def add_counterpart_relationship(self, cbox):
        #TODO remove this
        pass

#TODO class PythonPackage (for version control)