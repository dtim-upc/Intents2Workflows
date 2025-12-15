
from .python_implementation import PythonImplementation
from .python_parameter import PythonNumericParameter
from ..simple import nn_multidimensional
from ..core.expression import AlgebraicExpression



python_nn_tensor_implementation = PythonImplementation(
    name = "Python NN",
    baseImplementation = nn_multidimensional.nn_multi_learner_implementation,
    parameters=[
    ],
    python_module="tensorflow",
    python_function="NN",
    module_version='2.2.3',
    template="nn"
)

python_nn_tensor_applier_implementation = PythonImplementation(
    name= "Python NN applier",
    baseImplementation= nn_multidimensional.nn_multi_predictor_implementation,
    parameters= [
    ],
    python_module="tensorflow",
    python_function="NN",
    module_version='2.2.3',
    template="nn_predict"
) 