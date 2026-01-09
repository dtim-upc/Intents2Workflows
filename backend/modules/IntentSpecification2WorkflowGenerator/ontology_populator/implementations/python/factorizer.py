from ..simple.factorizer import factorizer_implemenation, factorizer_applier_implementation, columns_parameter
from .python_implementation import PythonImplementation
from .python_parameter import PythonTextParameter


columns_python_parameter = PythonTextParameter("columns", base_parameter=columns_parameter, default_value="$$CATEGORICAL_COLUMNS$$", control_parameter=True)
python_factorizer_implementation = PythonImplementation(
    name = "Python factorizer",
    baseImplementation = factorizer_implemenation,
    parameters=[
        columns_python_parameter
    ],
    python_module="pandas",
    python_function="factorize",
    python_dependences=[("pandas","2.2.3")],
    template="factorize"
)


python_factorizer_applier_implementation = PythonImplementation(
    name= "Python factorizer applier",
    baseImplementation= factorizer_applier_implementation,
    parameters= [
        columns_python_parameter
    ],
    python_module="pandas",
    python_function="factorize",
    python_dependences=[("pandas","2.2.3")],
    template="factorize_applier",
) 