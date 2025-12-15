from common import *
from ontology_populator.implementations.core import *
from .python_implementation import PythonImplementation
from .python_parameter import PythonTextParameter, PythonFactorParameter
from ..simple.io_multidimensional import tensor_data_reader_implementation, FORMATS

python_reader_tensor_implementation = PythonImplementation(
    name='Python Data Reader (tensor)',
    baseImplementation= tensor_data_reader_implementation,
    parameters=[
        PythonFactorParameter("format", levels={fmt:fmt for fmt in FORMATS},
                            base_parameter=next((param for param in tensor_data_reader_implementation.parameters.keys() if param.label == 'Format'), None),
                            default_value='CSV', control_parameter=True),
        PythonTextParameter("path",
                            base_parameter=next((param for param in tensor_data_reader_implementation.parameters.keys() if param.label == "Reader File"), None),
                            default_value=None)
    ],
    python_module="Custom",
    module_version="1.0.0",
    python_function="Custom",
    template="reader_multidimensional"
)