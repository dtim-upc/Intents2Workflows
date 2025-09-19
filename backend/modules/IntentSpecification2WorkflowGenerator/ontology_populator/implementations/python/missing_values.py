from .python_implementation import PythonImplementation, PythonTextParameter, PythonFactorParameter
from common import *
from ..simple.missing_values import missing_value_implementation, missing_value_applier_implementation

python_missing_value_implementation = PythonImplementation(
    name='Python Missing Value',
    baseImplementation=missing_value_implementation,
    parameters=[
        PythonTextParameter('numeric_columns',
                            base_parameter=next((p for p in missing_value_implementation.parameters.keys() if p.label == 'Numeric columns'),None),
                            default_value=None),
        PythonTextParameter('categorical_columns',
                            base_parameter=next((p for p in missing_value_implementation.parameters.keys() if p.label == 'Categorical columns'),None),
                            default_value=None),

        PythonFactorParameter('Numeric strategy', ["mean","drop"], 
                              base_parameter=next((p for p in missing_value_implementation.parameters.keys() if p.label == 'Numeric strategy'),None),
                              default_value = "mean"),
                              
        PythonFactorParameter('Factor strategy', ["most_frequent","drop"],
                              base_parameter=next((p for p in missing_value_implementation.parameters.keys() if p.label == 'Factor strategy'),None),
                              default_value = "most_frecuent"), #TODO drop is not present in sklearn, should be untranslatable
    ],
    python_module='sklearn',
    module_version='1.7.2',
    python_function='Custom',
    template="sklearn_imputation"
)


python_missing_value_applier_implementation = PythonImplementation(
    name='Python Missing Value (Applier)',
    baseImplementation=missing_value_applier_implementation,
    parameters=[
    ],
    python_module='sklearn',
    module_version='1.7.2',
    python_function='Custom',
    template="sklearn_imputation_applier",
)
