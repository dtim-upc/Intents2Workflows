from ..core import *
from common import *

mode = FactorParameter("mode", levels=["MinMax", "ZScore", "Decimal"])
max = Parameter("Maximum", XSD.float, default_value=1.0)
min = Parameter("Minimum", XSD.float, default_value=0)
cols = Parameter('Columns', RDF.List, '$$NUMERIC_COLUMNS$$')

scaling_learner_implementation = Implementation(
    name="Scaling",
    algorithm=cb.Normalization,
    parameters=[
        mode,
        max,
        min,
        cols

    ],
    input=[
        InputIOSpec([IOSpecTag(cb.TabularDataset)]),
    ],
    output=[
        OutputIOSpec([IOSpecTag(cb.NormalizedTabularDatasetShape)]),
        OutputIOSpec([IOSpecTag(cb.NormalizerModel)]),
    ],
    implementation_type=tb.LearnerImplementation
)

min_max_scaling_component = Component(
    name="Min Max scaler",
    implementation=scaling_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(mode, "MinMax"),
    ],
    rules={
        (cb.Classification, 2):[
            {'rule': cb.NotOutlieredDatasetShape, 'weight': 2},
            {'rule': cb.NotNormalDistributionDatasetShape, 'weight': 1}
        ],
        (cb.DataVisualization, 1): [
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    exposed_parameters=[
        min,
        max
    ],
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query='''
DELETE {
    ?column ?valueProperty ?value.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?valuePropetry rdfs:subPropertyOf dmop:ColumnValueInfo.
    ?column ?valueProperty ?value.
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:hasMinValue $parameter2;
            dmop:hasMaxValue $parameter3;
            dmop:isNormalized true.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:isFeature true .
}
            ''',
        ),
        Transformation(
            query='''
INSERT DATA {
    $output1 dmop:isNormalized true.
    $output2 cb:normalizationMode "MinMax";
             cb:newMin $parameter2;
             cb:newMax $parameter3.
}
            ''',
        ),
    ],
)

z_score_scaling_component = Component(
    name='Z-Score scaler',
    implementation=scaling_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(mode,"ZScore"),
    ],
    rules={
        (cb.Classification, 3):[
            {'rule': cb.NormalDistributionDatasetShape, 'weight': 2},
            {'rule': cb.OutlieredDatasetShape, 'weight': 1}
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
    ?column ?valueProperty ?value.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?valuePropetry rdfs:subPropertyOf dmop:ColumnValueInfo.
    ?column ?valueProperty ?value.
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:hasMeanValue 0;
            dmop:hasStandardDeviation 1;
            dmop:isNormalized true.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:isFeature true .
}
            ''',
        ),
        Transformation(
            query='''
INSERT DATA {
    $output1 dmop:isNormalized true.
    $output2 cb:normalizationMode "ZScore".
}
            ''',
        ),
    ],
)


decimal_scaling_component = Component(
    name='Decimal Scaler',
    implementation=scaling_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(mode, "Decimal"),
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.NotNormalDistributionDatasetShape, 'weight': 1},
            {'rule': cb.OutlieredDatasetShape, 'weight': 1}
        ],
        (cb.DataVisualization, 2): [
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query='''
DELETE {
    ?column ?valueProperty ?value.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?valuePropetry rdfs:subPropertyOf dmop:ColumnValueInfo.
    ?column ?valueProperty ?value.
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:isNormalized true.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:isFeature true .
}
            ''',
        ),
        Transformation(
            query='''
INSERT DATA {
    $output1 dmop:isNormalized true.
    $output2 cb:normalizationMode "Decimal".
}
            ''',
        ),
    ],
)

scailing_applier_output_data = OutputIOSpec([IOSpecTag(cb.NormalizedTabularDatasetShape)])
scaling_applier_implementation = Implementation(
    name="Scaling (applier)",
    algorithm=cb.Normalization,
    parameters=[
        cols
    ],
    input=[
        InputIOSpec([IOSpecTag(cb.NormalizerModel)]),
        InputIOSpec([IOSpecTag(cb.TestTabularDatasetShape)]),
    ],
    output=[
        scailing_applier_output_data, 
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart=scaling_learner_implementation
)
 

scaling_applier_component = Component( 
    name='Normalizer Applier',
    implementation=scaling_applier_implementation,
    transformations=[
        CopyTransformation(2, 1),
        #CopyTransformation(2, 2),
        Transformation(
            query='''
DELETE {
    ?column ?valueProperty ?value.
}
WHERE {
    $output2 dmop:hasColumn ?column.
    ?valuePropetry rdfs:subPropertyOf dmop:ColumnValueInfo.
    ?column ?valueProperty ?value.
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:hasMinValue $parameter2;
            dmop:hasMaxValue $parameter3;
            dmop:isNormalized true.
}
WHERE {
    $output2 dmop:hasColumn ?column.
    ?column dmop:isFeature true .
    $input1 cb:normalizationMode "MinMax".
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:hasMeanValue 0;
            dmop:hasStandardDeviation 1;
            dmop:isNormalized true.
}
WHERE {
    $output2 dmop:hasColumn ?column .
    ?column dmop:isFeature true .
    $input1 cb:normalizationMode "ZScore".
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:isNormalized true.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:isFeature true .
    $input1 cb:normalizationMode "Decimal".
}
            ''',
        ),
    ],
    counterpart=[
        min_max_scaling_component,
        z_score_scaling_component,
        decimal_scaling_component,
    ]
)