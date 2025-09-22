from common import *
from ontology_populator.implementations.core import *
from .python_implementation import PythonImplementation
from .python_parameter import PythonTextParameter
from ..simple.io import data_reader_implementation, data_writer_implementation

python_reader_implementation = PythonImplementation(
    name='Python Data Reader',
    baseImplementation= data_reader_implementation,
    parameters=[
        PythonTextParameter("format", 
                            base_parameter=next((param for param in data_reader_implementation.parameters.keys() if param.label == 'Format'), None),
                            default_value='CSV'),
        PythonTextParameter("path",
                            base_parameter=next((param for param in data_reader_implementation.parameters.keys() if param.label == "Reader File"), None),
                            default_value=None)
    ],
    python_module="Custom",
    module_version="1.0.0",
    python_function="Custom",
    template="reader"
)


python_writer_implementation = PythonImplementation(
    name='Python Data writer',
    baseImplementation= data_writer_implementation,
    parameters=[
        PythonTextParameter("path_or_buf",
                            base_parameter=next((param for param in data_writer_implementation.parameters.keys() if param.label == "Output path"), None),
                            default_value=None)
    ],
    python_module="pandas",
    module_version="2.2.3",
    python_function="DataFrame",
    template="writer"
)