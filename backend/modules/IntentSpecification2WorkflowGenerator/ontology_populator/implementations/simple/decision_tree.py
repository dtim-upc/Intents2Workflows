from ontology_populator.implementations.core import *
from common import *
from ..core.implementation import Implementation
from ..core.parameter import Parameter, FactorParameter

target = Parameter("Target", XSD.string, '$$LABEL_CATEGORICAL$$')
split_type = FactorParameter("Split type", ["Binary", "Multiway"])
min_samples = Parameter("Minimum samples per leaf", XSD.int, default_value=10)
split_criterion = FactorParameter("Split criterion", ["Gini", "Entropy", "LogLoss", "GainRatio"], default_value="Gini")
num_threads = Parameter("Number of threads", XSD.int)
splitter = FactorParameter("Splitter", ["Best", "Random"])
max_depth = Parameter("Maximum depth", XSD.int, None)

decision_tree_learner_implementation = Implementation(
    name='Decision Tree Learner',
    algorithm=cb.DecisionTree,
    parameters=[
        target,  
        split_type,
        min_samples,
        split_criterion,
        num_threads,
        splitter,
        max_depth,         
    ],
    input=[
        [cb.LabeledTabularDatasetShape, cb.TrainTabularDatasetShape]
    ],
    output=[
        cb.DecisionTreeModel,
    ],
    implementation_type=tb.LearnerImplementation,
)

binary_decision_tree_learner_component = Component(
    name='Binary Decision Tree Learner',
    implementation=decision_tree_learner_implementation,
    transformations=[
    ],
    exposed_parameters=[
       target,
    ],
    overriden_parameters=[
        ParameterSpecification(split_type, value="Binary")
    ]
)

decision_tree_predictor_implementation = Implementation(
    name='Decision Tree Predictor',
    algorithm=cb.DecisionTree,
    parameters=[
    ],
    input=[
        cb.DecisionTreeModel,
        cb.TestTabularDatasetShape,
    ],
    output=[
        cb.TabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart=decision_tree_learner_implementation,
)

decision_tree_predictor_component = Component(
    name='Decision Tree Predictor',
    implementation=decision_tree_predictor_implementation,

    transformations=[
        CopyTransformation(2, 1),
    ],
    counterpart=binary_decision_tree_learner_component,
)
