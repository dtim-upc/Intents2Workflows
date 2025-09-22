from typing import List, Union
from ontology_populator.implementations.core.expression import AlgebraicExpression
from ontology_populator.implementations.core.parameter import LiteralValue
from common import *
from ontology_populator.implementations.core.engine_parameter import EngineParameter, EngineFactorParameter, EngineNumericParameter, EngineTextParameter

class PythonParameter:
    def __init__(self, **kwargs):
        super().__init__(engine="Python", **kwargs)

class PythonNumericParameter(PythonParameter, EngineNumericParameter):
    def __init__(self, key:str, datatype:URIRef, expression:AlgebraicExpression, default_value:Union[URIRef, LiteralValue]):
        super().__init__(key=key, datatype=datatype, expression=expression, default_value=default_value)

class PythonTextParameter(PythonParameter, EngineTextParameter):
    def __init__(self, key:str, base_parameter:URIRef, default_value:Union[URIRef, LiteralValue]):
        super().__init__(key=key, base_parameter=base_parameter, default_value=default_value)

class PythonFactorParameter(PythonParameter, EngineFactorParameter):
    def __init__(self, key:str, levels: List[str], base_parameter:URIRef, default_value:Union[URIRef, LiteralValue]):
        super().__init__(key=key, levels=levels, base_parameter=base_parameter, default_value=default_value)