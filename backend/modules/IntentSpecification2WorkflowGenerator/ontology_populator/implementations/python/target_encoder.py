from ..simple.target_encoder_multidimensional import encoder_implemenation, encoder_applier_implementation
from .python_implementation import PythonImplementation
from .python_parameter import PythonTextParameter


python_target_encoder_implementation = PythonImplementation(
    name = "Python target encoder (tensor)",
    baseImplementation = encoder_implemenation,
    parameters=[
    ],
    python_module="numpy",
    python_function="custom",
    module_version='2.2.3',
    template="target_to_int_multidimensional"
)


python_target_encoder_applier_implementation = PythonImplementation(
    name= "Python target encoder applier (tensor)",
    baseImplementation= encoder_applier_implementation,
    parameters= [
    ],
    python_module="numpy",
    python_function="custom",
    module_version='2.2.3',
    template="target_to_int_multidimensional"
) 