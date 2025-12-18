from typing import List

from common import *
from ontology_populator.implementations.core import Implementation
from ontology_populator.implementations.core.engine_parameter import EngineParameter
from ontology_populator.implementations.core.engine_implementation import EngineImplementation


class PythonImplementation(EngineImplementation):

    def __init__(self, name: str, baseImplementation: Implementation, parameters: List[EngineParameter],
                 python_module, python_dependences, python_function, template, translation_condition = None, namespace: Namespace = cb) -> None:
        
        super().__init__(name,cb.Python,baseImplementation, parameters, translation_condition, namespace)
        self.python_module = python_module
        #self.python_module_version = module_version
        self.dependencies = python_dependences
        self.python_function = python_function
        self.template = template 

    def add_to_graph(self, g: Graph):

        g.add((self.uri_ref, tb.term('python_module'), Literal(self.python_module)))
        g.add((self.uri_ref, tb.term('python_function'), Literal(self.python_function)))
        #g.add((self.uri_ref, tb.term('python_version'), Literal(self.python_module_version)))
        g.add((self.uri_ref, tb.term('template'), Literal(self.template)))
        
        for dependency, version in self.dependencies:
            g.add((self.uri_ref, tb.term('python_dependency'), Literal(dependency)))

        for p in self.parameters:
            g.add((p.uri_ref, tb.isControlParameter, Literal(p.is_control_parameter)))

        return super().add_to_graph(g)
  