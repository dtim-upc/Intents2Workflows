from common import *
from ..core import *

svm_learner_implementation = Implementation(
    name='SVM Learner',
    algorithm=cb.SVM,
    parameters=[
        Parameter("SVM Class column", XSD.string, default_value="$$LABEL_CATEGORICAL$$"),
        Parameter("Overlapping Penalty", XSD.double),
        Parameter("Bias", XSD.double),
        Parameter("Power", XSD.double),
        Parameter("Gamma", XSD.double),
        FactorParameter("Kernel type", ['Polynomial', 'Sigmoid', 'RBF']),
    ],
    input=[
        InputIOSpec([IOSpecTag(cb.LabeledTabularDatasetShape), IOSpecTag(cb.TrainTabularDatasetShape), IOSpecTag(cb.NonNullTabularDatasetShape), 
         IOSpecTag(cb.NormalizedTabularDatasetShape), IOSpecTag(cb.NumericCategoricalTabularDatasetShape,1)]),
    ],
    output=[ 
        OutputIOSpec([IOSpecTag(cb.SVMModel)]),
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

sigmoid_svm_learner_component = Component(
    name='Sigmoid SVM Learner',
    implementation=svm_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Kernel type'), None), 'Sigmoid'),
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

svm_predictor_implementation = Implementation(
    name='SVM Predictor',
    algorithm=cb.SVM,
    parameters=[
    ],
    input=[
        InputIOSpec([IOSpecTag(cb.SVMModel)]),
        InputIOSpec([IOSpecTag(cb.TestTabularDatasetShape), IOSpecTag(cb.NonNullTabularDatasetShape), 
         IOSpecTag(cb.NormalizedTabularDatasetShape), IOSpecTag(cb.NumericCategoricalTabularDatasetShape,1)]), 
         #TODO add spec to filter out textual columns
         #TODO maybe each columns should be validated against "each" shape to decide what columns need each transformation. Not easy to implement (maybe in the future)
    ],
    output=[
        OutputIOSpec([IOSpecTag(cb.TabularDatasetShape)]),
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
        sigmoid_svm_learner_component,
        rbf_svm_learner_component,
    ],
)
