from typing import List, Union
from ontology_populator.implementations.core.expression import AlgebraicExpression
from ontology_populator.implementations.core.parameter import LiteralValue
from common import *
from ontology_populator.implementations.core.engine_parameter import EngineFactorParameter, EngineNumericParameter, EngineTextParameter, EngineSpecificParameter
from ontology_populator.implementations.core.parameter import Parameter

class KnimeParameter:
    def __init__(self, path, **kwargs):
        self.knime_path = path
        self.knime_key = kwargs.get('key')
        knime_key_clean = self.knime_key.replace("$", "")
        kwargs['key'] = f"{hash(self.knime_path)}-{knime_key_clean}" #to ensure unique URIs for parameters with same key but different path
        super().__init__(engine=cb.KNIME, **kwargs)

class KnimeSpecificParameter(KnimeParameter,EngineSpecificParameter):
    def __init__(self, key:str, datatype:URIRef, default_value:Union[URIRef, LiteralValue], path: str = 'model'):
        super().__init__(key=key, datatype=datatype, default_value=default_value, path=path)
        
class KnimeNumericParameter(KnimeParameter, EngineNumericParameter):
    def __init__(self, key:str, datatype:URIRef, expression:AlgebraicExpression, default_value:Union[URIRef, LiteralValue], path: str = 'model'):
        super().__init__(key=key, datatype=datatype, expression=expression, default_value=default_value, path=path)

class KnimeTextParameter(KnimeParameter, EngineTextParameter):
    def __init__(self, key:str, base_parameter:URIRef, default_value:Union[URIRef, LiteralValue], datatype=XSD.string, path: str = 'model'):
        super().__init__(key=key, base_parameter=base_parameter, default_value=default_value, path=path, datatype=datatype)

class KnimeFactorParameter(KnimeParameter, EngineFactorParameter):
    def __init__(self, key:str, levels: dict[str,str], base_parameter:URIRef, default_value:Union[URIRef, LiteralValue], datatype=XSD.string, path: str = 'model'):
        super().__init__(key=key, levels=levels, base_parameter=base_parameter, default_value=default_value, path=path, datatype=datatype)
