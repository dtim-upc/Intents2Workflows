from .knime_implementation import KnimeImplementation, KnimeBaseBundle, KnimeDefaultFeature
from .knime_parameter import KnimeTextParameter, KnimeFactorParameter, KnimeNumericParameter
from ..core.expression import AlgebraicExpression
from ..simple.scaling import scaling_applier_implementation, scaling_learner_implementation, mode, min, max, cols
from common import *

knime_normalizer_implementation = KnimeImplementation(
    name='Knime Normalizer (PMML)',
    base_implementation=scaling_learner_implementation,
    parameters=[
        KnimeFactorParameter( 'mode', levels={"1":"MinMax", "2":"ZScore", "3":"Decimal"}, base_parameter=mode, default_value=None),
        KnimeNumericParameter('newmin', XSD.float, expression=AlgebraicExpression(cb.COPY, min), default_value=0),
        KnimeNumericParameter('newmmax', XSD.float, expression=AlgebraicExpression(cb.COPY, max), default_value=1.0),
        KnimeTextParameter('columns', base_parameter=cols, default_value='', datatype=RDF.List )
    ],
    knime_node_factory='org.knime.base.node.preproc.pmml.normalize.NormalizerPMMLNodeFactory2',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature,
)

knime_normalizer_applier_implementation = KnimeImplementation(
    name='Knime Normalizer Apply (PMML)',
    base_implementation=scaling_applier_implementation,
    parameters=[],
    knime_node_factory='org.knime.base.node.preproc.pmml.normalize.NormalizerPMMLApplyNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature,
)