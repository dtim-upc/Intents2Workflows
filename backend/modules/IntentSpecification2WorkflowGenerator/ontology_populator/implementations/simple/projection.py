from common import *
from ..core import *

projection_numerical_learner_implementation = Implementation(
    name='Numerical Projection',
    algorithm=cb.DropColumns,
    parameters=[
        Parameter("Projected columns", RDF.List, default_value="$$NUMERIC_COLUMNS$$"),
        Parameter("Target Column", XSD.string, default_value="$$LABEL_CATEGORICAL$$"),
    ],
    input=[
        [cb.LabeledTabularDatasetShape, cb.TrainTabularDatasetShape],
    ],
    output=[
        cb.NumericOnlyTabularDatasetShape,
        cb.ProjectionModel,
    ],
    implementation_type=tb.LearnerImplementation,
)


numerical_transformation_query = '''
DELETE {
    ?column ?predicate ?object.
    $output1 dmop:hasColumn ?column.
    $output1 dmop:numberOfColumns ?numCols.
}
INSERT {
    $output1 dmop:numberOfColumns ?newNumCols.
}
WHERE {
    # Match non-numeric columns to delete
    $output1 dmop:hasColumn ?column.
    ?column dmop:isFeature true ;
            dmop:hasDataPrimitiveTypeColumn ?type ;
            dmop:hasColumnName ?label ;
            ?predicate ?object .

    FILTER(?type NOT IN (
        dmop:Float, dmop:Int, dmop:Number,
        dmop:Double, dmop:Long, dmop:Short, dmop:Integer
    ))

    BIND(5 AS ?newNumCols)
}
'''
 
projection_numerical_learner_component = Component(
    name='Projection numerical Learner',
    implementation=projection_numerical_learner_implementation,
    overriden_parameters=[
    ],
    exposed_parameters=[
    ],
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query=numerical_transformation_query),
        ],
)

projection_numerical_predictor_implementation = Implementation(
    name='Numeric projection Predictor',
    algorithm=cb.DropColumns,
    parameters=[],
    input=[
        cb.ProjectionModel,
        [cb.TestTabularDatasetShape, cb.NonNullTabularDatasetShape, (cb.NormalizedTabularDatasetShape,1), (cb.NumericCategoricalTabularDatasetShape,1)]
    ],
    output=[
        cb.NumericOnlyTabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart=projection_numerical_learner_implementation,
)

projection_numerical_predictor_component = Component(
    name='Projection numerical Predictor',
    implementation=projection_numerical_predictor_implementation,
    transformations=[
        CopyTransformation(2, 1),
        Transformation(
            query=numerical_transformation_query),
    ],
    counterpart=[
        projection_numerical_learner_component
    ],
)