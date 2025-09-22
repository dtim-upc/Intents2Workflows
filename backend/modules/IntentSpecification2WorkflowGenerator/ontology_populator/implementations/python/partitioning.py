from common import *
from .python_implementation import PythonImplementation
from .python_parameter import PythonNumericParameter
from ..simple import partitioning
from ..core.expression import AlgebraicExpression

base_params = partitioning.partitioning_implementation.parameters.keys()


python_partitioning_implementation = PythonImplementation(
    name='Python Data Partitioning',
    baseImplementation=partitioning.partitioning_implementation,
    parameters=[
        PythonNumericParameter('test_size', XSD.numeric, 
                               expression = AlgebraicExpression(cb.COPY, None), default_value=None),
        PythonNumericParameter("train_size", XSD.numeric, 
                               expression=AlgebraicExpression(cb.SUM,
                                                                AlgebraicExpression(cb.MUL,
                                                                    AlgebraicExpression(cb.EQ, 
                                                                                        next((p for p in base_params if p.label == "Size type"),None),
                                                                                        "Absolute"),
                                                                    next((p for p in base_params if p.label == "Count (Absolute size)"),None)),
                                                                AlgebraicExpression(cb.MUL,
                                                                    AlgebraicExpression(cb.EQ, 
                                                                                        next((p for p in base_params if p.label == "Size type"),None),
                                                                                        "Relative"),
                                                                    next((p for p in base_params if p.label == "Fraction (Relative size)"),None))),
                                default_value = 0.25),
                                                  
        PythonNumericParameter("random_state", XSD.int, 
                               expression=AlgebraicExpression(cb.COPY, next((p for p in base_params if p.label == "random_seed"),None)),default_value=None),
        PythonNumericParameter("shuffle", XSD.boolean,
                               expression=AlgebraicExpression(cb.EQ, next((p for p in base_params if p.label == "Sampling Method"),None), 'Random'),
                               default_value=True)
    ],
    python_module='sklearn.model_selection',
    module_version='1.7.2',
    python_function='train_test_split',
    template='basic_function'
)