from ..core import *
from common import *

missing_value_implementation = Implementation(
    name='Missing Value',
    algorithm=cb.MissingValueRemoval,
    parameters=[
        BaseParameter('Integer', XSD.string, None, condition='$$INTEGER_COLUMN$$'),
        BaseParameter('String', XSD.string, None, condition='$$STRING_COLUMN$$'),
        BaseParameter('Float', XSD.string, None, condition='$$FLOAT_COLUMN$$'),

        BaseParameter('Numeric columns', XSD.string,"$$NUMERIC_COLUMNS$$"),
        BaseParameter('Categorical columns', XSD.string,"$$CATEGORICAL_COLUMNS$$"),

        BaseFactorParameter('Numeric strategy', ["MeanImputation", "Drop"]),
        BaseFactorParameter('Factor strategy', ["MostFrequent","Drop"]),

    ],
    input=[
        cb.TabularDataset,
    ],
    output=[
        cb.NonNullTabularDatasetShape,
        cb.MissingValueModel,
    ],
    implementation_type=tb.LearnerImplementation,
)

mean_imputation_component = Component(
    name='Mean Imputation',
    implementation=missing_value_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in missing_value_implementation.parameters.keys()
                                     if param.label == 'Numeric strategy'), None),
                               'MeanImputation'),
        ParameterSpecification(next((param for param in missing_value_implementation.parameters.keys()
                                     if param.label == 'Factor strategy'), None),
                               'MostFrecuent'),
    ],
    exposed_parameters=[],
    rules={
        (cb.Classification, 2):[
            {'rule': cb.TabularDataset, 'weight': 1}
        ],
        (cb.DataVisualization, 1): [
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query='''
DELETE {
    ?column dmop:containsNulls false.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:containsNulls true.
}
'''),
    ],
)

drop_rows_component = Component(
    name='Drop Rows with Missing Values',
    implementation=missing_value_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in missing_value_implementation.parameters.keys()
                                     if param.label == 'Numeric strategy'), None),
                               'Drop'),
        ParameterSpecification(next((param for param in missing_value_implementation.parameters.keys()
                                     if param.label == 'Factor strategy'), None),
                               'Drop'),
    ],
    exposed_parameters=[],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.LowMVTabularDatasetShape, 'weight': 2}
        ],
        (cb.DataVisualization, 1): [
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query='''
DELETE {
    ?column dmop:containsNulls false.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:containsNulls true.
}
'''),
        Transformation(
            query='''
DELETE {
    $output1 dmop:numberOfRows ?rows1.
}
WHERE {
    $output1 dmop:numberOfRows ?rows1.
}
''',
        ),
        Transformation(
            query='''
INSERT DATA {
    $output2 cb:removesProperty dmop:numberOfRows.
}
''',
        ),
    ],
)


missing_value_applier_implementation = Implementation(
    name='Missing Value (Applier)',
    algorithm=cb.MissingValueRemoval,
    parameters=[
    ],
    input=[
        cb.MissingValueModel,
        cb.TestTabularDatasetShape,
    ],
    output=[
        cb.NonNullTabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,

)

missing_value_applier_component = Component(
    name='Missing Value Management Applier',
    implementation=missing_value_applier_implementation,
    overriden_parameters=[],
    exposed_parameters=[],
    transformations=[
        CopyTransformation(2, 1),
        Transformation(
            query='''
DELETE {
    $output2 ?property ?value.
}
WHERE {
    $output1 cb:removesProperty ?property.
    $output2 ?property ?value.
}
''',
        ),
    ],
    counterpart=[
        mean_imputation_component,
        drop_rows_component,
    ]
)
