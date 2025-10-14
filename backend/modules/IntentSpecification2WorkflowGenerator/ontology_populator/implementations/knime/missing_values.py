from .knime_implementation import KnimeImplementation, KnimeBaseBundle, KnimeDefaultFeature
from .knime_parameter import KnimeFactorParameter, KnimeSpecificParameter, KnimeTextParameter
from ..simple.missing_values import missing_value_implementation, missing_value_applier_implementation, missing_value_applier_implementation_output_port
from ..core import *
from common import *

numeric_levels = {
    'org.knime.base.node.preproc.pmml.missingval.handlers.DoubleMeanMissingCellHandlerFactory': "MeanImputation",
    'org.knime.base.node.preproc.pmml.missingval.pmml.RemoveRowMissingCellHandlerFactory': "Drop"
}

string_levels = {
    'org.knime.base.node.preproc.pmml.missingval.handlers.MostFrequentValueMissingCellHandlerFactory': 'MostFrequent',
    'org.knime.base.node.preproc.pmml.missingval.pmml.RemoveRowMissingCellHandlerFactory':'Drop'
}

knime_missing_value_implementation = KnimeImplementation(
    name='Knime Missing Value',
    base_implementation=missing_value_implementation,
    parameters=[
        KnimeFactorParameter('factoryID', levels=numeric_levels,
                           base_parameter=next((p for p in missing_value_implementation.parameters.keys() if p.label == 'Numeric strategy'),None),
                           default_value=None, path='model/dataTypeSettings/org.knime.core.data.def.IntCell'),
        KnimeFactorParameter('factoryID', levels=string_levels,
                           base_parameter=next((p for p in missing_value_implementation.parameters.keys() if p.label == 'Factor strategy'),None),
                           default_value=None, path='model/dataTypeSettings/org.knime.core.data.def.StringCell'),
        KnimeFactorParameter('factoryID', levels=numeric_levels,
                           base_parameter=next((p for p in missing_value_implementation.parameters.keys() if p.label == 'Numeric strategy'),None), 
                           default_value=None, path='model/dataTypeSettings/org.knime.core.data.def.DoubleCell'),

        KnimeSpecificParameter('$$SKIP$$', XSD.string, None, 
                       path='model/dataTypeSettings/org.knime.core.data.def.IntCell/settings'),
        KnimeSpecificParameter('$$SKIP$$', XSD.string, None, 
                       path='model/dataTypeSettings/org.knime.core.data.def.StringCell/settings'),
        KnimeSpecificParameter('$$SKIP$$', XSD.string, None, 
                       path='model/dataTypeSettings/org.knime.core.data.def.DoubleCell/settings'),

        KnimeSpecificParameter('$$SKIP$$', XSD.string, None, path='model/columnSettings'),
    ],
    knime_node_factory='org.knime.base.node.preproc.pmml.missingval.compute.MissingValueHandlerNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
)

knime_missing_value_applier_implementation = KnimeImplementation(
    name='Knime Missing Value (Applier)',
    base_implementation=missing_value_applier_implementation,
    parameters=[
    ],
    knime_node_factory='org.knime.base.node.preproc.pmml.missingval.apply.MissingValueApplyNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature,
    output_ports=[
        cb.NONE,
        missing_value_applier_implementation_output_port.get_uri(missing_value_applier_implementation.uri_ref)
    ]
)
