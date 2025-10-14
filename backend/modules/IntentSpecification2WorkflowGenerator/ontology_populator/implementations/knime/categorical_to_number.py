from .knime_implementation import KnimeImplementation, KnimeBaseBundle, KnimeDefaultFeature
from .knime_parameter import KnimeTextParameter, KnimeSpecificParameter
from ..core import *
from common import *
from ..simple.factorizer import factorizer_implemenation, factorizer_applier_implementation, columns_parameter, factorizer_applier_output_spec_data

knime_categorizer_implementation = KnimeImplementation(
    name='KNIME Categorizer',
    base_implementation=factorizer_implemenation, 
    parameters=[
        KnimeSpecificParameter("filter-type", XSD.string, 'STANDARD', path='model/column-filter'),
        KnimeTextParameter('included_names',base_parameter=columns_parameter, default_value="$$CATEGORICAL_COLUMNS$$",datatype=RDF.List, path='model/column-filter'),
        KnimeSpecificParameter("excluded_names", RDF.List, {}, path='model/column-filter'),
        KnimeSpecificParameter('enforce_option', XSD.string, 'EnforceInclusion', path='model/column-filter'),
        KnimeSpecificParameter('pattern', XSD.string, "", path='model/column-filter/name_pattern'),
        KnimeSpecificParameter('type', XSD.string, "Wildcard", path='model/column-filter/name_pattern'),
        KnimeSpecificParameter('caseSensitive', XSD.boolean, True, path='model/column-filter/name_pattern'),
        KnimeSpecificParameter('excludeMatching', XSD.boolean, False, path='model/column-filter/name_pattern'),
        KnimeSpecificParameter('org.knime.core.data.IntValue', XSD.boolean, False, path='model/column-filter/datatype/typelist'),
        KnimeSpecificParameter('org.knime.core.data.StringValue', XSD.boolean, False, path='model/column-filter/datatype/typelist'),
        KnimeSpecificParameter('org.knime.core.data.DoubleValue', XSD.boolean, False, path='model/column-filter/datatype/typelist'),
        KnimeSpecificParameter('org.knime.core.data.BooleanValue', XSD.boolean, False, path='model/column-filter/datatype/typelist'),
        KnimeSpecificParameter('org.knime.core.data.LongValue', XSD.boolean, False, path='model/column-filter/datatype/typelist'),
        KnimeSpecificParameter("org.knime.core.data.date.DateAndTimeValue", XSD.boolean, False, path='model/column-filter/datatype/typelist'),
        KnimeSpecificParameter("append_columns", XSD.boolean, False, path='model'),
        KnimeSpecificParameter("column_suffix", XSD.string, " (to number)", path='model'),
        KnimeSpecificParameter("start_index", XSD.int, 0, path='model'),
        KnimeSpecificParameter('increment', XSD.int, 1, path='model'),
        KnimeSpecificParameter("max_categories", XSD.int, 50, path='model'),
        KnimeSpecificParameter("datacell", XSD.string, "org.knime.core.data.MissingCell", path='model/default_value'),
        KnimeSpecificParameter('$$SKIP$$', XSD.string, None, path='model/default_value/org.knime.core.data.MissingCell'),
        KnimeSpecificParameter("datacell", XSD.string, "org.knime.core.data.MissingCell", path='model/map_missing_to'),
        KnimeSpecificParameter('$$SKIP$$', XSD.string, None, path='model/map_missing_to/org.knime.core.data.MissingCell'),
    ],
    knime_node_factory='org.knime.base.node.preproc.colconvert.categorytonumber2.CategoryToNumberNodeFactory2',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature,
)


knime_categorizer_applier_implementation = KnimeImplementation(
    name='KNIME Categorizer (Applier)',
    base_implementation=factorizer_applier_implementation,
    parameters=[
        KnimeSpecificParameter("append_columns", XSD.boolean, False, path='model'),
        KnimeSpecificParameter("column_suffix", XSD.string, " (to number)", path='model'),
    ],
    knime_node_factory='org.knime.base.node.preproc.colconvert.categorytonumber.CategoryToNumberApplyNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature,
    output_ports=[
        cb.NONE,
        factorizer_applier_output_spec_data.get_uri(factorizer_applier_implementation.uri_ref)
    ]
)
