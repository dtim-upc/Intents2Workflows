from common import *
from ..core.expression import AlgebraicExpression
from .python_parameter import PythonNumericParameter
from .python_implementation import PythonImplementation
from ..simple.dbscan import dbscan_implementation

python_dbscan_implementation = PythonImplementation(
    name="Python DBSCAN",
    baseImplementation=dbscan_implementation,
    parameters=[
        PythonNumericParameter("eps", datatype=XSD.float,
                               expression=AlgebraicExpression(cb.COPY, next((param for param in dbscan_implementation.parameters.keys() if param.label == 'epsilon'),None)),
                               default_value=0.5),
        PythonNumericParameter("min_samples", datatype=XSD.float,
                               expression=AlgebraicExpression(cb.COPY, next((param for param in dbscan_implementation.parameters.keys() if param.label == 'minimum samples'),None)),
                               default_value=5),
        
    ],
    python_module='sklearn.cluster',
    module_version='1.7.2',
    python_function='DBSCAN',
    template='basic_sklearn_fitpredict_function'
)