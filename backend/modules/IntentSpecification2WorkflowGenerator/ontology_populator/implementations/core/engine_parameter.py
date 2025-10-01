from typing import Union
from rdflib import URIRef

from .parameter import Parameter, FactorParameter, LiteralValue
from .expression import AlgebraicExpression

import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from common import *

class EngineParameter(Parameter):
    def __init__(self, engine: str, key: str, datatype: URIRef,
                 default_value: Union[URIRef, LiteralValue],**kwargs) -> None:
        super().__init__(key,datatype, default_value,**kwargs)
        self.engine = engine

class EngineNumericParameter(EngineParameter):
    def __init__(self, engine:str, key: str, datatype: URIRef,
                     expression: AlgebraicExpression, default_value: Union[URIRef, LiteralValue]) -> None: 
        super().__init__(engine,key, datatype, default_value)
        self.expression = expression #Numeric parameters can be derived from multiple parameters, so no base parameter defined

class EngineTextParameter(EngineParameter):
    def __init__(self, engine:str, key: str, base_parameter: Parameter, 
                 default_value: Union[URIRef, LiteralValue], datatype = XSD.string) -> None:
        super().__init__(engine=engine, key=key, datatype=datatype,  default_value=default_value)
        self.base_parameter = base_parameter #Textual parameters are assumed (for now) to have a one by one mapping to a base parameter

class EngineFactorParameter(EngineTextParameter):
    def __init__(self, engine:str, key: str, levels: list[str], base_parameter: FactorParameter, 
                 default_value: Union[URIRef, LiteralValue]):
        super().__init__(engine=engine,key=key,base_parameter=base_parameter,default_value=default_value)
        self.levels_dict = levels
        #EngineFactor parameter is defined as a text parameter with finite values

class EngineSpecificParameter(EngineParameter):
    def __init__(self, engine:str, key: str, datatype: URIRef, default_value: Union[URIRef, LiteralValue]):
        super().__init__(engine=engine,key=key, datatype=datatype,default_value=default_value)
