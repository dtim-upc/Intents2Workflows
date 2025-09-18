from common import *
from ..core import *

svm_learner_implementation = Implementation(
    name='SVM Learner',
    algorithm=cb.SVM,
    parameters=[
        BaseParameter("SVM Class column", XSD.string, value="$$LABEL_CATEGORICAL$$"),
        BaseParameter("Overlapping Penalty", XSD.double),
        BaseParameter("Bias", XSD.double),
        BaseParameter("Power", XSD.double),
        BaseParameter("Gamma", XSD.double),
        BaseFactorParameter("Kernel type", ['Polynomial', 'Sigmoid', 'RBF']),
    ],
    input=[
        [cb.LabeledTabularDatasetShape, cb.TrainTabularDatasetShape, cb.NonNullTabularDatasetShape, 
         (cb.NormalizedTabularDatasetShape,1), (cb.NumericCategoricalTabularDatasetShape,1)],
    ],
    output=[
        cb.SVMModel,
    ],
    implementation_type=tb.LearnerImplementation,
)

polynomial_svm_learner_component = Component(
    name='Polynomial SVM Learner',
    implementation=svm_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Kernel type'), None), 'Polynomial'),
    ],
    exposed_parameters=[
        next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'SVM Class column'), None),
    ],
    transformations=[
        Transformation(
            query='''
INSERT {
    $output1 cb:setsClassColumnName "Prediction (?label)" .
}
WHERE {
    $input1 dmop:hasColumn ?column .
    ?column dmop:isLabel true ;
            dmop:hasColumnName ?label .
}
            ''',
        ),
    ],
)

hypertangent_svm_learner_component = Component(
    name='HyperTangent SVM Learner',
    implementation=svm_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Kernel type'), None), 'HyperTangent'),
    ],
    exposed_parameters=[
        next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'SVM Class column'), None),
    ],
    transformations=[
        Transformation(
            query='''
INSERT DATA{
    $output1 cb:setsClassColumnName $parameter1 .
}
            ''',
        ),
    ],
)

rbf_svm_learner_component = Component(
    name='RBF SVM Learner',
    implementation=svm_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Kernel type'), None), 'RBF'),
    ],
    exposed_parameters=[
        next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'SVM Class column'), None),
    ],
    transformations=[
        Transformation(
            query='''
INSERT DATA{
    $output1 cb:setsClassColumnName $parameter1 .
}
            ''',
        ),
    ],
)

svm_predictor_implementation = Implementation(
    name='SVM Predictor',
    algorithm=cb.SVM,
    parameters=[
    ],
    input=[
        cb.SVMModel,
        [cb.TestTabularDatasetShape, cb.NonNullTabularDatasetShape, (cb.NormalizedTabularDatasetShape,1), (cb.NumericCategoricalTabularDatasetShape,1)]
    ],
    output=[
        cb.TabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart=svm_learner_implementation,
)

svm_predictor_component = Component(
    name='SVM Predictor',
    implementation=svm_predictor_implementation,
    transformations=[
        CopyTransformation(2, 1),
        Transformation(
            query='''
INSERT {
    $output1 dmop:hasColumn _:labelColumn .
    _:labelColumn a dmop:Column ;
        dmop:isLabel true;
      dmop:hasName $parameter1.
}
WHERE {
    $input1 cb:setsClassColumnName ?classColumnName .
}
            ''',
        ),
    ],
    counterpart=[
        polynomial_svm_learner_component,
        hypertangent_svm_learner_component,
        rbf_svm_learner_component,
    ],
)
