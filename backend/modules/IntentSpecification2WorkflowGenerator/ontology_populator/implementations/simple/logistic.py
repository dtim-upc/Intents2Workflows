from common import *
from ..core import *

logistic_learner_implementation = Implementation(
    name='Logistic Regression Learner',
    algorithm=cb.LogisticRegression,
    parameters=[
        Parameter("Class column", XSD.string, default_value="$$LABEL_CATEGORICAL$$"),
    ],
    input=[
        InputIOSpec([IOSpecTag(cb.LabeledTabularDatasetShape), IOSpecTag(cb.TrainTabularDatasetShape), IOSpecTag(cb.NonNullTabularDatasetShape), 
         IOSpecTag(cb.NormalizedTabularDatasetShape), IOSpecTag(cb.NumericCategoricalTabularDatasetShape)]),
    ],
    output=[ 
        OutputIOSpec([IOSpecTag(cb.LogisticModelShape)]),
    ],
    implementation_type=tb.LearnerImplementation,
)

logistic_learner_component = Component(
    name='Logistic Learner component',
    implementation=logistic_learner_implementation,
    overriden_parameters=[
    ],
    exposed_parameters=[
        next((param for param in logistic_learner_implementation.parameters.keys() if param.label == 'Class column'), None),
    ],
    transformations=[],
)

logistic_predictor_implementation = Implementation(
    name='Logistic Predictor',
    algorithm=cb.LogisticRegression,
    parameters=[
    ],
    input=[
        InputIOSpec([IOSpecTag(cb.LogisticModelShape)]),
        InputIOSpec([IOSpecTag(cb.TestTabularDatasetShape), IOSpecTag(cb.NonNullTabularDatasetShape), 
         IOSpecTag(cb.NormalizedTabularDatasetShape), IOSpecTag(cb.NumericCategoricalTabularDatasetShape,1)]), 
    ],
    output=[
        OutputIOSpec([IOSpecTag(cb.TabularDatasetShape)]),
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart=logistic_learner_implementation,
)

logistic_predictor_component = Component(
    name='Logistic Predictor component',
    implementation=logistic_predictor_implementation,
    transformations=[],
    counterpart=[
        logistic_learner_component,
    ],
)
