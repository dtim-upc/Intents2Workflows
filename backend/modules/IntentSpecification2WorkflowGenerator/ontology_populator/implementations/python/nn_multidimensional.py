
from .python_implementation import PythonImplementation
from .python_parameter import PythonFactorParameter
from ..simple import nn_multidimensional



python_nn_tensor_implementation = PythonImplementation(
    name = "Python NN",
    baseImplementation = nn_multidimensional.nn_multi_learner_implementation,
    parameters=[
        PythonFactorParameter("type",{'FFNN':'FeedForward',"RNN":'Recurrent',"CNN":'Convolutional','LSTM':"LSTM"}, 
                              base_parameter=next((param for param in nn_multidimensional.nn_multi_learner_implementation.parameters.keys() if param.label == 'NN type'),None),
                              default_value="CNN", control_parameter=True)
    ],
    python_module="tensorflow",
    python_function="NN",
    python_dependences=[("tensorflow", '2.2.3')],
    template="nn"
)

python_nn_tensor_applier_implementation = PythonImplementation(
    name= "Python NN applier",
    baseImplementation= nn_multidimensional.nn_multi_predictor_implementation,
    parameters= [
    ],
    python_module="tensorflow",
    python_function="NN",
    python_dependences=[("tensorflow", '2.2.3')],
    template="nn_predict"
) 