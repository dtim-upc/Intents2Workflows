from common import *
from .knime_implementation import KnimeImplementation, KnimeBaseBundle, KnimeParameter, KnimeDefaultFeature
from ..core import *

nn_learner_implementation = KnimeImplementation(
    name='NN Learner',
    algorithm=cb.NN,
    parameters=[
        KnimeParameter("Class column", XSD.string, "$$LABEL$$", 'classcol'),
        KnimeParameter("NN type", XSD.string, None, 'nn_type'),
    ],
    input=[
        [cb.LabeledTabularDatasetShape, cb.TrainTabularDatasetShape, cb.NormalizedTabularDatasetShape, cb.NonNullTabularDatasetShape],
    ],
    output=[
        cb.NNModel,
    ],
    implementation_type=tb.LearnerImplementation,
    knime_node_factory='org.knime.base.node.mine.svm.predictor2.SVMPredictorNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
)

feedforward_learner_component = Component(
    name='FeedForward NN Learner',
    implementation=nn_learner_implementation,
    overriden_parameters=[
         ParameterSpecification(next((param for param in nn_learner_implementation.parameters.keys() if param.knime_key == 'nn_type'), None), 'FeedForward'),
    ],
    exposed_parameters=[
        next((param for param in nn_learner_implementation.parameters.keys() if param.knime_key == 'classcol'),None)
    ],
    transformations=[
    ],
)

recurrent_learner_component = Component(
    name='Recurrent NN Learner',
    implementation=nn_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in nn_learner_implementation.parameters.keys() if param.knime_key == 'nn_type'), None), 'Recurrent'),
    ],
    exposed_parameters=[
        next((param for param in nn_learner_implementation.parameters.keys() if param.knime_key == 'classcol'),None)
    ],
    transformations=[
    ],
)

convolutional_learner_component = Component(
    name='Convolutional NN Learner',
    implementation=nn_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in nn_learner_implementation.parameters.keys() if param.knime_key == 'nn_type'), None), 'Convolutional'),
    ],
    exposed_parameters=[
        next((param for param in nn_learner_implementation.parameters.keys() if param.knime_key == 'classcol'),None)
    ],
    transformations=[
    ],
)

lstm_learner_component = Component(
    name='LSTM NN Learner',
    implementation=nn_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in nn_learner_implementation.parameters.keys() if param.knime_key == 'nn_type'), None), 'LSTM'),
    ],
    exposed_parameters=[
        next((param for param in nn_learner_implementation.parameters.keys() if param.knime_key == 'classcol'),None)
    ],
    transformations=[
    ],
)

nn_predictor_implementation = KnimeImplementation(
    name='NN Predictor',
    algorithm=cb.NN,
    parameters=[
        KnimeParameter("Prediction column name", XSD.string, "Prediction ($$LABEL$$)", 'prediction column name'),
        KnimeParameter("Change prediction", XSD.boolean, False, 'change prediction'),
        KnimeParameter("Add probabilities", XSD.boolean, False, 'add probabilities'),
        KnimeParameter("Class probability suffix", XSD.string, "", 'class probability suffix'),
    ],
    input=[
        cb.NNModel,
        [cb.TestTabularDatasetShape,cb.NormalizedTabularDatasetShape, cb.NonNullTabularDatasetShape]
    ],
    output=[
        cb.TabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart=nn_learner_implementation,
    knime_node_factory='org.knime.base.node.mine.svm.predictor2.SVMPredictorNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
)

nn_predictor_component = Component(
    name='NN Predictor',
    implementation=nn_predictor_implementation,
    transformations=[

    ],
    counterpart=[
        feedforward_learner_component,
        recurrent_learner_component,
        convolutional_learner_component,
        lstm_learner_component
    ],
)
