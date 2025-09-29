from common import *
from .python_implementation import PythonImplementation
from .python_parameter import PythonTextParameter
from ..simple.projection import projection_numerical_learner_implementation, projection_numerical_predictor_implementation

python_projection_numerical_learner_implementation = PythonImplementation(
    name='Python Numerical Projection',
    baseImplementation=projection_numerical_learner_implementation,
    parameters=[
        PythonTextParameter("columns",
                            base_parameter=next((p for p in projection_numerical_learner_implementation.parameters.keys() if p.label == 'Projected columns'),None),
                            default_value=[]),
        PythonTextParameter("Target",
                            base_parameter=next((p for p in projection_numerical_learner_implementation.parameters.keys() if p.label == 'Target Column'),None),
                            default_value="", control_parameter=True),
    ],
    python_module='pandas',
    module_version='2.2.3',
    python_function='custom',
    template="projection_train"
)

python_projection_numerical_predictor_implementation = PythonImplementation(
    name='Python Numeric projection Predictor',
    baseImplementation=projection_numerical_predictor_implementation,
    parameters=[],
    python_module='pandas',
    module_version='2.2.3',
    python_function='custom',
    template="projection_predict"

)

