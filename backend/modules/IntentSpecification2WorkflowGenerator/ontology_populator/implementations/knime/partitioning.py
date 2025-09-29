from common import *
from .knime_implementation import KnimeBaseBundle, KnimeImplementation, KnimeDefaultFeature
from .knime_parameter import KnimeFactorParameter, KnimeNumericParameter, KnimeTextParameter
from ..simple.partitioning import partitioning_implementation
from ..core.expression import AlgebraicExpression


knime_partitioning_implementation = KnimeImplementation(
    name='Knime Data Partitioning',
    base_implementation=partitioning_implementation,
    parameters=[
        KnimeFactorParameter("method", levels={'Absolute':'Absolute', 'Relative':'Relative'}, 
                             base_parameter=next((param for param in partitioning_implementation.parameters.keys() if param.label == "Size type"),None),
                             default_value=None),
        KnimeFactorParameter("samplingMethod", levels={'Random':'Random', 'First':'First'}, 
                             base_parameter=next((param for param in partitioning_implementation.parameters.keys() if param.label == "Sampling Method"),None),
                             default_value=None),
        KnimeNumericParameter("fraction", XSD.double,
                              expression=AlgebraicExpression(cb.COPY, next((param for param in partitioning_implementation.parameters.keys() if param.label == "Fraction (Relative size)"),None)), 
                             default_value=0.8),
        KnimeNumericParameter("count", XSD.int, 
                              expression=AlgebraicExpression(cb.COPY, next((param for param in partitioning_implementation.parameters.keys() if param.label == "Count (Absolute size)"),None)),
                              default_value=100),
        KnimeNumericParameter("random_seed", XSD.int, 
                              expression=AlgebraicExpression(cb.COPY, next((param for param in partitioning_implementation.parameters.keys() if param.label == "Random seed"),None)),
                              default_value=None),
        KnimeTextParameter("class_column", 
                           base_parameter= next((param for param in partitioning_implementation.parameters.keys() if param.label == "Class columns"),None),
                           default_value=None),
    ],
    knime_node_factory='org.knime.base.node.preproc.partition.PartitionNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
)