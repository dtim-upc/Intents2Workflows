from common import *
from .python_implementation import PythonImplementation
from .python_parameter import PythonFactorParameter, PythonTextParameter
from ..simple.missing_values import missing_value_implementation, missing_value_applier_implementation, num_param, factor_param

python_num_param = PythonTextParameter('numeric_columns',base_parameter=num_param,default_value=None, control_parameter=True)

python_factor_param = PythonTextParameter('categorical_columns',base_parameter=factor_param,default_value=None, control_parameter=True)


python_missing_value_implementation = PythonImplementation(
    name='Python Missing Value',
    baseImplementation=missing_value_implementation,
    parameters=[
        PythonFactorParameter('Factor strategy', {"most_frequent":"MostFrequent","drop":"Drop"},
                              base_parameter=next((p for p in missing_value_implementation.parameters.keys() if p.label == 'Factor strategy'),None),
                              default_value = "most_frequent", control_parameter=True),

        PythonFactorParameter('Numeric strategy', {"mean":"MeanImputation","drop":"Drop"}, 
                            base_parameter=next((p for p in missing_value_implementation.parameters.keys() if p.label == 'Numeric strategy'),None),
                            default_value = "mean", control_parameter=True), #TODO redefine control_parameter concept (kwargs vs args) and the availability through all steps
        python_num_param,
        python_factor_param,
    ],
    python_module='sklearn.impute',
    python_dependences=[('scikit-learn', '1.7.2')],
    python_function='SimpleImputer',
    template="sklearn_missings",
)


python_missing_value_applier_implementation = PythonImplementation(
    name='Python Missing Value (Applier)',
    baseImplementation=missing_value_applier_implementation,
    parameters=[
        python_num_param,
        python_factor_param
    ],
    python_module='sklearn.impute',
    python_dependences=[('scikit-learn', '1.7.2')],
    python_function='SimpleImputer',
    template="sklearn_missings_applier",
)
