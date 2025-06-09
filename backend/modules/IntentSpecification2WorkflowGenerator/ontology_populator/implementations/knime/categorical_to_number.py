from .knime_implementation import KnimeImplementation, KnimeParameter, KnimeBaseBundle, KnimeDefaultFeature
from ..core import *
from common import *

categorizer_implementation = KnimeImplementation(
    name='Categorizer',
    algorithm=cb.DataManagement,
    parameters=[
        KnimeParameter('Filter type', XSD.string, 'STANDARD', "filter-type", path='model/column-filter'),
        KnimeParameter('Inclusions', RDF.List, '$$CATEGORICAL_COLUMNS$$', 'included_names', path='model/column-filter'),
        KnimeParameter('Exclusions', RDF.List, {}, "excluded_names", path='model/column-filter'),
        KnimeParameter('Enforce inclusion', XSD.string, 'EnforceInclusion', 'enforce_option', path='model/column-filter'),
        KnimeParameter('Name pattern', XSD.string, "", 'pattern', path='model/column-filter/name_pattern'),
        KnimeParameter('Pattern type', XSD.string, "Wildcard", 'type', path='model/column-filter/name_pattern'),
        KnimeParameter('Case sensitive', XSD.boolean, True, 'caseSensitive', path='model/column-filter/name_pattern'),
        KnimeParameter('Exclude matching', XSD.boolean, False, 'excludeMatching',path='model/column-filter/name_pattern'),
        KnimeParameter('Integer', XSD.boolean, False, 'org.knime.core.data.IntValue',path='model/column-filter/datatype/typelist'),
        KnimeParameter('String', XSD.boolean, False, 'org.knime.core.data.StringValue',path='model/column-filter/datatype/typelist'),
        KnimeParameter('Double', XSD.boolean, False, 'org.knime.core.data.DoubleValue',path='model/column-filter/datatype/typelist'),
        KnimeParameter('Boolean', XSD.boolean, False, 'org.knime.core.data.BooleanValue',path='model/column-filter/datatype/typelist'),
        KnimeParameter('Long', XSD.boolean, False, 'org.knime.core.data.LongValue',path='model/column-filter/datatype/typelist'),
        KnimeParameter('Date', XSD.boolean, False, "org.knime.core.data.date.DateAndTimeValue",path='model/column-filter/datatype/typelist'),
        KnimeParameter('Append columns', XSD.boolean, False, "append_columns", path='model'),
        KnimeParameter('Column suffix', XSD.string, " (to number)", "column_suffix", path='model'),
        KnimeParameter('Start index', XSD.int, 0, "start_index", path='model'),
        KnimeParameter('Increment', XSD.int, 1, "increment", path='model'),
        KnimeParameter('Max categories', XSD.int, 50, "max_categories", path='model'),
        KnimeParameter('Default value', XSD.string, "org.knime.core.data.MissingCell", "datacell", path='model/default_value'),
        KnimeParameter('Default value missing', XSD.string, None, '$$SKIP$$', path='model/default_value/org.knime.core.data.MissingCell'),
        KnimeParameter('Default value 2', XSD.string, "org.knime.core.data.MissingCell", "datacell", path='model/map_missing_to'),
        KnimeParameter('Default value missing 2', XSD.string, None, '$$SKIP$$', path='model/map_missing_to/org.knime.core.data.MissingCell'),

    ],
    input=[
        cb.TabularDataset,
    ],
    output=[
        cb.NumericCategoricalTabularDatasetShape,
        cb.NumericCategoricalModel,
    ],
    implementation_type=tb.LearnerImplementation,
    knime_node_factory='org.knime.base.node.preproc.colconvert.categorytonumber2.CategoryToNumberNodeFactory2',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature,
)

categorizer_component = Component(
    name='Categorizer  Component',
    implementation=categorizer_implementation,
    overriden_parameters=[],
    exposed_parameters=[],
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query='''
DELETE {
  ?column dmop:hasDataPrimitiveTypeColumn ?oldDatatype .
}
INSERT {
  ?column dmop:hasDataPrimitiveTypeColumn xsd:int . 
}
WHERE {
  $output2 dmop:hasColumn ?column .
  ?column dmop:isCategorical true .
  ?column dmop:datatype ?oldDatatype . 
}
''',
        ),
    ],
)


categorizer_applier_implementation = KnimeImplementation(
    name='Categorizer (Applier)',
    algorithm=cb.DataManagement,
    parameters=[
        KnimeParameter('Append columns', XSD.boolean, False, "append_columns", path='model'),
        KnimeParameter('Column suffix', XSD.string, " (to number)", "column_suffix", path='model'),
    ],
    input=[
        cb.NumericCategoricalModel,
        cb.TestTabularDatasetShape
    ],
    output=[
        cb.NumericCategoricalModel,
        cb.NumericCategoricalTabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    knime_node_factory='org.knime.base.node.preproc.colconvert.categorytonumber.CategoryToNumberApplyNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature,
)

categorizer_applier_component = Component(
    name='Categorizer Applier Component',
    implementation=categorizer_applier_implementation,
    overriden_parameters=[],
    exposed_parameters=[],
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(2, 2),
        Transformation(
            query='''
DELETE {
  ?column dmop:hasDataPrimitiveTypeColumn ?oldDatatype .
}
INSERT {
  ?column dmop:hasDataPrimitiveTypeColumn xsd:int . 
}
WHERE {
  $output2 dmop:hasColumn ?column .
  ?column dmop:isCategorical true .
  ?column dmop:datatype ?oldDatatype . 
}
''',
        ),
    ],
    counterpart=[
        categorizer_component
    ]
)
