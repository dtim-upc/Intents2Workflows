from common import *
from ..core import *

xgboost_learner_implementation = Implementation(
    name='XGBoost Learner',
    algorithm=cb.XGBoost,
    parameters=[
        Parameter("Target Column", XSD.string, "$$LABEL_CATEGORICAL$$"),
        Parameter('Numeric columns', XSD.string,"$$NUMERIC_COLUMNS$$"),
        FactorParameter('Booster', ["tree","linear",'dart']),
        Parameter("Sample weight", XSD.string),
        Parameter("Boosting rounds", XSD.int),
        Parameter("Number of threads", XSD.int),
        Parameter("Random seed", XSD.int),
        Parameter("Base score", XSD.double),
        FactorParameter("Objective", ["multi:softprob","binary:logistic"] ),
        Parameter("Lambda", XSD.double),
        Parameter("Alpha", XSD.double),
        FactorParameter("Updater", ['Shotgun','CoordDescent']),
        FactorParameter("Feature selector", ['cyclic', 'shuffle', 'random', 'greedy', 'thrifty']),
        Parameter("Top K", XSD.int),
        Parameter("Eta", XSD.double),
        Parameter("Gamma", XSD.double),
        Parameter("Max Depth", XSD.int),
        Parameter("Min child weight", XSD.double),
        Parameter("Max delta step", XSD.double),
        Parameter("Subsample", XSD.double),
        Parameter("Col sample by tree", XSD.double),
        Parameter("Col sample by level", XSD.double),
        Parameter("Col sample by node", XSD.double),
        FactorParameter("Tree method", ['auto', 'exact', 'approx', 'hist']),
        Parameter("Sketch Eps", XSD.double),
        Parameter("Scale Pos Weight", XSD.double),
        FactorParameter("Grow policy", ['depthwise', 'lossguide']),
        Parameter("Max Leaves", XSD.int),
        Parameter("Max Bin", XSD.int),
        FactorParameter('Sample type', ['uniform', 'weighted']),
        FactorParameter('Normalize type', ['tree', 'forest']),
        Parameter("Rate drop", XSD.double),
        Parameter("One drop", XSD.boolean),
        Parameter("Skip drop", XSD.double),
    ],
    input=[
        [cb.LabeledTabularDatasetShape, cb.TrainTabularDatasetShape, cb.NumericOnlyTabularDatasetShape],
    ],
    output=[
        cb.XGBoostModel, 
    ],
    implementation_type=tb.LearnerImplementation,
)

xgboost_tree_learner_component = Component(
    name='XGBoost Tree Learner',
    implementation=xgboost_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in xgboost_learner_implementation.parameters.keys() if param.label == 'Booster'), None), 'tree'),
    ],
    exposed_parameters=[
        next((param for param in xgboost_learner_implementation.parameters.keys() if param.label == 'Target Column'), None),
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

xgboost_linear_learner_component = Component(
    name='XGBoost Linear Learner',
    implementation=xgboost_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in xgboost_learner_implementation.parameters.keys() if param.label == 'Booster'), None), 'linear'),
    ],
    exposed_parameters=[
        next((param for param in xgboost_learner_implementation.parameters.keys() if param.label == 'Target Column'), None),
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

xgboost_dart_learner_component = Component(
    name='XGBoost Dart Learner',
    implementation=xgboost_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in xgboost_learner_implementation.parameters.keys() if param.label == 'Booster'), None), 'dart'),
    ],
    exposed_parameters=[
        next((param for param in xgboost_learner_implementation.parameters.keys() if param.label == 'Target Column'), None),
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



xgboost_predictor_implementation = Implementation(
    name='XGBoost Predictor',
    algorithm=cb.XGBoost,
    parameters=[
    ],
    input=[
        cb.XGBoostModel,
        [cb.TestTabularDatasetShape, cb.NumericOnlyTabularDatasetShape]
    ],
    output=[
        cb.TabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart= [
        xgboost_learner_implementation,
    ],
)

xgboost_predictor_component = Component(
    name='XGBoost Predictor',
    implementation=xgboost_predictor_implementation,
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
        xgboost_linear_learner_component,
        xgboost_tree_learner_component,
        xgboost_dart_learner_component,
    ],
)
