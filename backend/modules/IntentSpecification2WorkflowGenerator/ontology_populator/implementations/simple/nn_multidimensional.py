from common import *
from ..core import *

nn_multi_learner_implementation = Implementation(
    name='NN Multidimensional Learner',
    algorithm=cb.NN,
    parameters=[
        Parameter("Label array", XSD.string, "$$LABEL$$"),
        Parameter("NN type", XSD.string, None),
    ],
    input=[
        [cb.LabeledTensorDatasetShape, cb.TrainTabularDatasetShape],
    ],
    output=[
        cb.NNModel,
    ],
    implementation_type=tb.LearnerImplementation,
)

feedforward_multi_learner_component = Component(
    name='FeedForward NN Multidimensional Learner',
    implementation=nn_multi_learner_implementation,
    overriden_parameters=[
         ParameterSpecification(next((param for param in nn_multi_learner_implementation.parameters.keys() if param.label == 'NN type'), None), 'FeedForward'),
    ],
    exposed_parameters=[
        next((param for param in nn_multi_learner_implementation.parameters.keys() if param.label == 'Label array'),None)
    ],
    transformations=[
    ],
)

recurrent_multi_learner_component = Component(
    name='Recurrent NN Multidimensional Learner',
    implementation=nn_multi_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in nn_multi_learner_implementation.parameters.keys() if param.label == 'NN type'), None), 'Recurrent'),
    ],
    exposed_parameters=[
        next((param for param in nn_multi_learner_implementation.parameters.keys() if param.label == 'Label array'),None)
    ],
    transformations=[
    ],
)

convolutional_multi_learner_component = Component(
    name='Convolutional NN Multidimensional Learner',
    implementation=nn_multi_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in nn_multi_learner_implementation.parameters.keys() if param.label == 'NN type'), None), 'Convolutional'),
    ],
    exposed_parameters=[
        next((param for param in nn_multi_learner_implementation.parameters.keys() if param.label == 'Label array'),None)
    ],
    transformations=[
    ],
)

lstm_multi_learner_component = Component(
    name='LSTM NN Multidimensional Learner',
    implementation=nn_multi_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in nn_multi_learner_implementation.parameters.keys() if param.label == 'NN type'), None), 'LSTM'),
    ],
    exposed_parameters=[
        next((param for param in nn_multi_learner_implementation.parameters.keys() if param.label == 'Label array'),None)
    ],
    transformations=[
    ],
)

nn_multi_predictor_implementation = Implementation(
    name='NN Multidimensional Predictor',
    algorithm=cb.NN,
    parameters=[
        Parameter("Prediction array name", XSD.string, "Prediction ($$LABEL$$)", 'prediction array name'),
        Parameter("Change prediction", XSD.boolean, False, 'change prediction'),
        Parameter("Add probabilities", XSD.boolean, False, 'add probabilities'),
        Parameter("Class probability suffix", XSD.string, "", 'class probability suffix'),
    ],
    input=[
        cb.NNModel,
        [cb.TestTabularDatasetShape,cb.NormalizedTabularDatasetShape, cb.NonNullTabularDatasetShape]
    ],
    output=[
        cb.TabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart=nn_multi_learner_implementation,
)

nn_multi_predictor_component = Component(
    name='NN Multidimensional Predictor',
    implementation=nn_multi_predictor_implementation,
    transformations=[

    ],
    counterpart=[
        feedforward_multi_learner_component,
        recurrent_multi_learner_component,
        convolutional_multi_learner_component,
        lstm_multi_learner_component
    ],
)
