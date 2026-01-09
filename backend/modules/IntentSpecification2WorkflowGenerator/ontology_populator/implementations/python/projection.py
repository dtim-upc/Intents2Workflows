from common import *
from .python_implementation import PythonImplementation
from .python_parameter import PythonTextParameter
from ..simple.projection import projection_learner_implementation, projection_predictor_implementation

python_projection_learner_implementation = PythonImplementation(
    name='Python Numerical Projection',
    baseImplementation=projection_learner_implementation,
    parameters=[
        PythonTextParameter("columns",
                            base_parameter=next((p for p in projection_learner_implementation.parameters.keys() if p.label == 'Projected columns'),None),
                            default_value=[]),
        PythonTextParameter("Target",
                            base_parameter=next((p for p in projection_learner_implementation.parameters.keys() if p.label == 'Target Column'),None),
                            default_value="", control_parameter=True),
    ],
    python_module='pandas',
    python_dependences=[("pandas","2.2.3")],
    python_function='custom',
    template="projection"
)


python_projection_predictor_implementation = PythonImplementation(
    name='Python Numeric projection Predictor',
    baseImplementation=projection_predictor_implementation,
    parameters=[
        PythonTextParameter("columns",
                            base_parameter=next((p for p in projection_predictor_implementation.parameters.keys() if p.label == 'Projected columns'),None),
                            default_value=[]),
        PythonTextParameter("Target",
                            base_parameter=next((p for p in projection_predictor_implementation.parameters.keys() if p.label == 'Target Column'),None),
                            default_value="", control_parameter=True),
    ],
    python_module='pandas',
    python_dependences=[("pandas","2.2.3")],
    python_function='custom',
    template="projection"

)

