from common import *
from ..core.expression import AlgebraicExpression
from .python_parameter import PythonNumericParameter, PythonTextParameter, PythonFactorParameter
from .python_implementation import PythonImplementation
from ..simple import logistic

python_logistic_learner_implementation = PythonImplementation(
    name='Python Logistic Learner',
    baseImplementation = logistic.logistic_learner_implementation,
    parameters=[
        PythonTextParameter(key="Target",
                        base_parameter= next((param for param in logistic.logistic_learner_implementation.parameters.keys() if param.label == 'Class column'),None),
                        default_value="target", control_parameter=True), 
    ],
    python_module='sklearn.linear_model',
    python_dependences=[('scikit-learn', '1.7.2')],
    python_function='LogisticRegression',
    template='sklearn_train'
)


python_logistic_predictor_implementation = PythonImplementation(
    name='Python Logistic Predictor',
    parameters=[
    ],
    baseImplementation=logistic.logistic_predictor_implementation,
    python_module='sklearn.linear_model',
    python_dependences=[('scikit-learn', '1.7.2')],
    python_function='LogisticRegression',
    template='sklearn_predict'
    
) 
