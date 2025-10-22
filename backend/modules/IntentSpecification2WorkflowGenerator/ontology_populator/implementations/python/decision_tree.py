from .python_implementation import PythonImplementation
from .python_parameter import PythonNumericParameter, PythonTextParameter, PythonFactorParameter
from ..simple.decision_tree import decision_tree_learner_implementation, decision_tree_predictor_implementation, target, split_type, split_criterion, min_samples, splitter, max_depth
from ..core.expression import AlgebraicExpression
from common import *

python_decision_tree_implementation = PythonImplementation(
    name="Python decision tree",
    baseImplementation=decision_tree_learner_implementation,
    parameters=[
        PythonTextParameter("Target", base_parameter=target, default_value="target", control_parameter=True),
        PythonFactorParameter("criterion", levels={"gini":"Gini", "entropy":"Entropy", "log_loss":"LogLoss"},
                              base_parameter= split_criterion, default_value="gini"),
        PythonFactorParameter("split_method", levels={"Binary":"Binary"}, base_parameter=split_type, default_value="Binary", control_parameter=True),
        PythonNumericParameter("min_samples_leaf", XSD.int, 
                               expression=AlgebraicExpression(cb.COPY, min_samples), default_value=1),
        PythonFactorParameter("splitter", levels={"best":"Best", "random":"Random"}, base_parameter=splitter, default_value="best"),
        PythonNumericParameter("max_depth", XSD.int, 
                               expression=AlgebraicExpression(cb.COPY, max_depth), default_value=None)
    ],
    python_module='sklearn.tree',
    module_version='1.7.2',
    python_function='DecisionTreeClassifier',
    template='sklearn_train'
) 
 
python_decision_tree_predictor_implementation = PythonImplementation(
    name= "Python decision tree predictor",
    baseImplementation= decision_tree_predictor_implementation,
    parameters=[],
    python_module='sklearn.tree',
    module_version='1.7.2',
    python_function='DecisionTreeClassifier',
    template='sklearn_predict'
)

