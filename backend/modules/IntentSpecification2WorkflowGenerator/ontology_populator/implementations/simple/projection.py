from common import *
from ..core import *

projection_learner_implementation = Implementation(
    name='Numerical Projection',
    algorithm=cb.DropColumns,
    parameters=[
        Parameter("Projected columns", RDF.List),
        Parameter("Target Column", XSD.string, default_value="$$LABEL_CATEGORICAL$$"),
    ],
    input=[
        cb.TabularDataset,
    ],
    output=[
        cb.NumericOnlyTabularDatasetShape,
    ],
    implementation_type=tb.LearnerImplementation,
)


numerical_transformation_query = '''
DELETE {
    ?column ?predicate ?object.
    $output0 dmop:hasColumn ?column.
    $output0 dmop:numberOfColumns ?numCols.
}
INSERT {
    $output0 dmop:numberOfColumns ?newNumCols.
}
WHERE {
    # Match non-numeric columns to delete
    $output0 dmop:hasColumn ?column.
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
    implementation=projection_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next(p for p in projection_learner_implementation.parameters if p.label == "Projected columns"), "$$NUMERIC_AND_TARGET_COLUMNS$$"),
    ],
    exposed_parameters=[
    ],
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query=numerical_transformation_query),
        ],
)

projection_predictor_implementation = Implementation(
    name='Numeric projection Predictor',
    algorithm=cb.DropColumns,
    parameters=[
        Parameter("Projected columns", RDF.List),
        Parameter("Target Column", XSD.string, default_value="$$LABEL_CATEGORICAL$$"),
    ],
    input=[
        cb.TabularDataset
    ],
    output=[
        cb.NumericOnlyTabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart=projection_learner_implementation,
)

projection_numerical_predictor_component = Component(
    name='Projection numerical Predictor',
    implementation=projection_predictor_implementation,
    overriden_parameters=[
        ParameterSpecification(next(p for p in projection_predictor_implementation.parameters if p.label == "Projected columns"), "$$NUMERIC_AND_TARGET_COLUMNS$$"),
    ],
    exposed_parameters=[
    ],
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query=numerical_transformation_query),
    ],
    counterpart=[
        projection_numerical_learner_component
    ],
) 