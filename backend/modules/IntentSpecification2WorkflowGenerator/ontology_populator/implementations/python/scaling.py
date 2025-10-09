from common import *
from .python_implementation import PythonImplementation
from .python_parameter import PythonNumericParameter, PythonTextParameter, PythonFactorParameter
from ..simple.scaling import scaling_learner_implementation, scaling_applier_implementation, mode, min, max, cols
from ..core.expression import AlgebraicExpression



python_cols = PythonTextParameter("columns", base_parameter=cols, default_value="", control_parameter=True)

python_minmax_scaling_implementation = PythonImplementation(
    name="Python min max scaler",
    baseImplementation=scaling_learner_implementation,
    parameters=[
        python_cols,
        PythonNumericParameter("feature_range.min", XSD.float,
                               expression=AlgebraicExpression(cb.COPY, min), default_value=0),
        PythonNumericParameter("feature_range.max", XSD.float,
                               expression=AlgebraicExpression(cb.COPY, max), default_value=1),
    ],
    python_module='sklearn.preprocessing',
    module_version='1.7.2',
    python_function='MinMaxScaler',
    template='sklearn_scaling',
    translation_condition= AlgebraicExpression(cb.EQ, mode, "MinMax")
) 

python_zscore_scaling_implementation = PythonImplementation(
    name="Python zscore scaler",
    baseImplementation=scaling_learner_implementation,
    parameters=[
        python_cols
    ],
    python_module='sklearn.preprocessing',
    module_version='1.7.2',
    python_function='StandardScaler',
    template='sklearn_scaling',
    translation_condition=AlgebraicExpression(cb.EQ, mode, "ZScore")
)


python_scaling_applier_implementation = PythonImplementation(
    name= "Python scaler (applier)",
    baseImplementation=scaling_applier_implementation,
    parameters=[],
    python_module='sklearn.preprocessing',
    module_version='1.7.2',
    python_function='Scaler', #does not matter in this case
    template='sklearn_scaling_applier'
)