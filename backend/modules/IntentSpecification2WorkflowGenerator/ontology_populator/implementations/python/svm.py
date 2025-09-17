from common import *
from ..core import *
from .python_implementation import PythonImplementation, PythonParameter, PythonNumericParameter, PythonFactorParameter, AlgebraicExpression
from ..simple import svm

python_svm_learner_implementation = PythonImplementation(
    name='Python SVM Learner',
    baseImplementation = svm.svm_learner_implementation,
    parameters=[
        PythonParameter("Target", XSD.string, 
                        #base_parameter= next((param for param in svm.svm_learner_implementation.parameters.keys() if param.label == 'SVM Class column'),None),
                        default_value="target"), 
        PythonNumericParameter("C", XSD.double,
                        expression = AlgebraicExpression(cb.SUM, 0 ,next((param for param in svm.svm_learner_implementation.parameters.keys() if param.label == 'Overlapping Penalty'),0)),
                        default_value=1.1),
        PythonNumericParameter("coef0", XSD.double,
                        expression = AlgebraicExpression(cb.SUM, 0 ,next((param for param in svm.svm_learner_implementation.parameters.keys() if param.label == 'Bias'),0)),
                        default_value=0.0),
        PythonNumericParameter("degree", XSD.integer,
                        expression = AlgebraicExpression(cb.SUM, 0 ,next((param for param in svm.svm_learner_implementation.parameters.keys() if param.label == 'Power'),0)),
                        default_value=3),
        PythonNumericParameter("gamma", XSD.double,
                        expression = AlgebraicExpression(cb.SUM, 0 ,next((param for param in svm.svm_learner_implementation.parameters.keys() if param.label == 'Gamma'),0)),
                        default_value='scale'),
        PythonFactorParameter("kernel", ['poly', 'sigmoid', 'rbf'],
                        base_parameter=next((param for param in svm.svm_learner_implementation.parameters.keys() if param.label == 'Kernel type'),None),
                        default_value='rbf'),
    ],
    python_package='sklearn',
    python_module='svm',
    python_function='SVC'
)


python_svm_predictor_implementation = PythonImplementation(
    name='Python SVM Predictor',
    parameters=[
    ],
    baseImplementation=svm.svm_predictor_implementation,
    python_package='sklearn',
    python_module=None,
    python_function='fit'
    
)
