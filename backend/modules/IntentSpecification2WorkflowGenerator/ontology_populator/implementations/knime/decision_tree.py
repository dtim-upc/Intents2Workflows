from ontology_populator.implementations.core.expression import AlgebraicExpression
from common import *
from .knime_implementation import KnimeImplementation, KnimeBaseBundle, KnimeDefaultFeature
from .knime_parameter import KnimeFactorParameter, KnimeSpecificParameter, KnimeTextParameter, KnimeNumericParameter
from ..simple.decision_tree import decision_tree_learner_implementation, decision_tree_predictor_implementation, target, split_criterion, min_samples, num_threads, split_type

knime_decision_tree_learner_implementation = KnimeImplementation(
    name='Knime Decision Tree Learner',
    base_implementation=decision_tree_learner_implementation,
    parameters=[
        KnimeTextParameter('classifyColumn', base_parameter=target, default_value='$$LABEL_CATEGORICAL$$'),
        KnimeSpecificParameter('numverRecordsToView', XSD.int, 10000,),
        KnimeNumericParameter('minNumberRecordsPerNode', XSD.int,
                              expression=AlgebraicExpression(cb.COPY,min_samples), 
                              default_value=10 ),
        KnimeSpecificParameter('pruningMethod', XSD.string, "No pruning"),
        KnimeSpecificParameter('enableReducedErrorPruning', XSD.boolean, True),
        KnimeFactorParameter('splitQualityMeasure', levels={"Gini index":"Gini", "Gain ratio":"GainRatio"}, base_parameter=split_criterion, default_value="Gini index" ),
        KnimeSpecificParameter('splitAverage', XSD.boolean, True),
        KnimeNumericParameter('numProcessors', XSD.int, 
                              expression=AlgebraicExpression(cb.COPY, num_threads),
                              default_value=1),
        KnimeSpecificParameter('maxNumNominalValues', XSD.int, 10),
        KnimeNumericParameter('binaryNominalSplit', XSD.boolean, 
                              expression=AlgebraicExpression(cb.EQ, split_type, True),
                              default_value=False),
        KnimeSpecificParameter('FilterNominalValuesFromParent', XSD.boolean, False),
        KnimeSpecificParameter('skipColumnsWithoutDomain', XSD.boolean, False),
        KnimeSpecificParameter('CFG_NOTRUECHILD', XSD.string, "returnNullPrediction"),
        KnimeSpecificParameter('CFG_MISSINGSTRATEGY', XSD.string, "lastPrediction"),
        KnimeSpecificParameter('useFirstSplitColumn', XSD.boolean, False),
        KnimeSpecificParameter('firstSplitColumn', XSD.string, None),
    ],
    knime_node_factory='org.knime.base.node.mine.decisiontree2.learner2.DecisionTreeLearnerNodeFactory3',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
)


knime_decision_tree_predictor_implementation = KnimeImplementation(
    name='Decision Tree Predictor',
    base_implementation=decision_tree_predictor_implementation,
    parameters=[
        KnimeSpecificParameter("UseGainRatio", XSD.int, 20000),
        KnimeSpecificParameter("ShowDistribution", XSD.boolean, True, ),
        KnimeSpecificParameter("prediction column name", XSD.string, "Prediction ($$LABEL$$)"),
        KnimeSpecificParameter("change prediction", XSD.boolean, False),
        KnimeSpecificParameter("class probability suffix", XSD.string, ""),
    ],
    knime_node_factory='org.knime.base.node.mine.decisiontree2.predictor2.DecTreePredictorNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
)
