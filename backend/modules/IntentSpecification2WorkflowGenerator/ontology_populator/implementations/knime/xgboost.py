from common import *
from .knime_implementation import KnimeImplementation, KnimeXGBoostBundle, KnimeParameter, KnimeXGBoostFeature
from ..core import *

xgboost_linear_learner_implementation = KnimeImplementation(
    name='XGBoost Linear Learner',
    algorithm=cb.XGBoost,
    parameters=[
        KnimeParameter("Target column", XSD.string, "$$LABEL_CATEGORICAL$$", 'targetColumn',path='model/options'),
        KnimeParameter("Overlapping Penalty", XSD.string, None, 'weightColumn',path='model/options'),
        KnimeParameter("Boosting rounds", XSD.int, 100, 'boostingRounds',path='model/options'),
        KnimeParameter("Number of threads", XSD.int, 4, 'numThreads',path='model/options'),
        KnimeParameter("Manual number of threads", XSD.boolean, False, 'manualNumThreads',path='model/options'),
        KnimeParameter("Use static seed", XSD.boolean, False, 'useStaticSeed',path='model/options'),
        KnimeParameter("Static seed", XSD.int, 0, 'staticSeed', path='model/options'),
        KnimeParameter("BaseScore", XSD.double, 0.5, 'baseScore', path='model/options'),
        KnimeParameter("Objective", XSD.string, "multi:softprob", "identifier", path='model/options/objective' ),
        KnimeParameter("Filter type", XSD.string, "STANDARD", "filter-type", path='model/options/featureFilter'),
        KnimeParameter("Enforce option", XSD.string, "EnforceInclusion", "enforce_option", path='model/options/featureFilter'),
        KnimeParameter('Numeric columns', RDF.List, '$$NUMERIC_COLUMNS$$', 'included_names', path='model/options/featureFilter'),
        KnimeParameter('Other columns', XSD.string, None, '$$SKIP$$', path='model/options/featureFilter/excluded_names'),
        KnimeParameter("Lambda", XSD.double, 0.3, "lambda", path='model/booster'),
        KnimeParameter("Alpha", XSD.double, 0.3, "alpha", path='model/booster'),
        KnimeParameter("Updater", XSD.string, "CoordDescent", "updater", path='model/booster'),
        KnimeParameter("Feature selector", XSD.string, "Greedy", "featureSelector", path='model/booster'),
        KnimeParameter("Top K", XSD.int, 0, "topK", path='model/booster')
    ],
    input=[
        [cb.LabeledTabularDatasetShape, cb.TrainTabularDatasetShape, (cb.NonNullTabularDatasetShape,2)],
    ],
    output=[
        cb.XGBoostModel,
    ],
    implementation_type=tb.LearnerImplementation,
    knime_node_factory='org.knime.xgboost.base.nodes.learner.classification.XGBLinearClassificationLearnerNodeFactory2',
    knime_bundle=KnimeXGBoostBundle,
    knime_feature=KnimeXGBoostFeature
)

xgboost_linear_learner_component = Component(
    name='XGBoost Learner',
    implementation=xgboost_linear_learner_implementation,
    overriden_parameters=[
    ],
    exposed_parameters=[
        next((param for param in xgboost_linear_learner_implementation.parameters.keys() if param.knime_key == 'targetColumn'), None),
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


xgboost_predictor_implementation = KnimeImplementation(
    name='XGBoost Predictor',
    algorithm=cb.XGBoost,
    parameters=[
        KnimeParameter("SVM Prediction column name", XSD.string, "Prediction ($$LABEL$$)", 'predictionColumnName'),
        KnimeParameter("Change prediction", XSD.boolean, False, 'changePredictionColumnName'),
        KnimeParameter("Add probabilities", XSD.boolean, False, 'appendProbabilities'),
        KnimeParameter("Class probability suffix", XSD.string, "", 'probabilitySuffix'),
        KnimeParameter("Unknown categorical as missing", XSD.boolean, False, 'unknownAsMissing'),
        KnimeParameter('Batch size', XSD.int, 10000, "batchSize")
    ],
    input=[
        cb.XGBoostModel,
        [cb.TestTabularDatasetShape, (cb.NonNullTabularDatasetShape,2)]
    ],
    output=[
        cb.TabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart=xgboost_linear_learner_implementation,
    knime_node_factory='org.knime.xgboost.base.nodes.predictor.XGBClassificationPredictorNodeFactory',
    knime_bundle=KnimeXGBoostBundle,
    knime_feature=KnimeXGBoostFeature,
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
    ],
)

