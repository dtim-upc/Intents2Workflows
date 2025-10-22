from common import *
from .knime_implementation import KnimeImplementation, KnimeBaseBundle, KnimeDefaultFeature
from .knime_parameter import KnimeFactorParameter, KnimeTextParameter, KnimeNumericParameter, KnimeSpecificParameter
from ..simple.projection import projection_learner_implementation, projection_predictor_implementation

knime_projection_parameters = [
    KnimeSpecificParameter("filter-type", XSD.string, "STANDARD", path='model/column-filter'),
    KnimeSpecificParameter("enforce_option", XSD.string, "EnforceInclusion", path='model/column-filter'),
    KnimeSpecificParameter('$$SKIP$$', XSD.string, None, path='model/column-filter/excluded_names'),

]

knime_projection_learner_implementation = KnimeImplementation(
    name='KNIME Projection',
    base_implementation=projection_learner_implementation,
    parameters=[
        *knime_projection_parameters,
        KnimeTextParameter('included_names', 
                    base_parameter= next((param for param in projection_learner_implementation.parameters if param.label == 'Projected columns'), None),
                    default_value="[]", path='model/column-filter', datatype=RDF.List),
    ],
    knime_node_factory="org.knime.base.node.preproc.filter.column.DataColumnSpecFilterNodeFactory",
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
)

knime_projection_applier_implementation = KnimeImplementation(
    name='KNIME Projection Applier',
    base_implementation=projection_predictor_implementation,
    parameters=[
        *knime_projection_parameters,
        KnimeTextParameter('included_names', 
                    base_parameter= next((param for param in projection_predictor_implementation.parameters if param.label == 'Projected columns'), None),
                    default_value="[]", path='model/column-filter', datatype=RDF.List),
    ],
    knime_node_factory="org.knime.base.node.preproc.filter.column.DataColumnSpecFilterNodeFactory",
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
)
