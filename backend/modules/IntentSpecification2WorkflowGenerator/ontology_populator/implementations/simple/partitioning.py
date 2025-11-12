from common import *
from ..core import *

partitioning_implementation = Implementation(
    name='Data Partitioning',
    algorithm=cb.Partitioning,
    parameters=[
        FactorParameter("Size type", ['Absolute', 'Relative']),
        FactorParameter("Sampling Method", ['Random', 'First']),
        Parameter("Fraction (Relative size)", XSD.double, 0.25),
        Parameter("Count (Absolute size)", XSD.int, 10),
        Parameter("Random seed", XSD.string),
        Parameter("Class columns", XSD.string),
    ],
    input=[
        InputIOSpec([IOSpecTag(cb.TabularDatasetShape)]),
    ],
    output=[
        OutputIOSpec([IOSpecTag(cb.TrainTabularDatasetShape), IOSpecTag(cb.TabularDatasetShape)]),
        OutputIOSpec([IOSpecTag(cb.TestTabularDatasetShape)]),
    ],
)

implementation_parameters = partitioning_implementation.parameters

random_relative_train_test_split_component = Component(
    name='Random Relative Train-Test Split',
    implementation=partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(list(implementation_parameters.keys())[0], "Relative"),
        ParameterSpecification(list(implementation_parameters.keys())[1], "Random")
    ],
    exposed_parameters=[
        list(implementation_parameters.keys())[2],
        list(implementation_parameters.keys())[4],
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(1, 2),
        Transformation(
            query='''
DELETE {
    $output1 dmop:numberOfRows ?rows1.
    $output2 dmop:numberOfRows ?rows1.
}
INSERT {
    $output1 dmop:numberOfRows ?newRows1 .
    $output1 dmop:isTrainDataset True .
    $output2 dmop:numberOfRows ?newRows2 .
    $output2 dmop:isTestDataset True .
}
WHERE {
    $output1 dmop:numberOfRows ?rows1.
    BIND(xsd:integer(ROUND(?rows1 * (1 - $parameter3))) AS ?newRows2)
    BIND(?rows1 - ?newRows2 AS ?newRows1)
}
''',
        ),
    ],
)

random_absolute_train_test_split_component = Component(
    name='Random Absolute Train-Test Split',
    implementation=partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(list(implementation_parameters.keys())[0], "Absolute"),
        ParameterSpecification(list(implementation_parameters.keys())[1], "Random")
    ],
    exposed_parameters=[
        list(implementation_parameters.keys())[3],
        list(implementation_parameters.keys())[4],
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(1, 2),
        Transformation(
            query='''
DELETE {
    $output1 dmop:numberOfRows ?rows1.
    $output2 dmop:numberOfRows ?rows1.
}
INSERT {
    $output1 dmop:numberOfRows ?newRows1 .
    $output1 dmop:isTrainDataset True .
    $output2 dmop:numberOfRows ?newRows2 .
    $output2 dmop:isTestDataset True .
}
WHERE {
    $output1 dmop:numberOfRows ?rows1.
    BIND(IF( ?rows1 - $parameter4>0, ?rows1 - $parameter4, 0 ) AS ?newRows2)
    BIND(?rows1 - ?newRows2 AS ?newRows1)
}
''',
        ),
    ],
)

top_relative_train_test_split_component = Component(
    name='Top K Relative Train-Test Split',
    implementation=partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(list(implementation_parameters.keys())[0], "Relative"),
        ParameterSpecification(list(implementation_parameters.keys())[1], "First"),
    ],
    exposed_parameters=[
        list(implementation_parameters.keys())[2],
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(1, 2),
        Transformation(
            query='''
DELETE {
    $output1 dmop:numberOfRows ?rows1.
    $output2 dmop:numberOfRows ?rows1.
}
INSERT {
    $output1 dmop:numberOfRows ?newRows1 .
    $output1 dmop:isTrainDataset True .
    $output2 dmop:numberOfRows ?newRows2 .
    $output2 dmop:isTestDataset True .
}
WHERE {
    $output1 dmop:numberOfRows ?rows1.
    BIND(xsd:integer(ROUND(?rows1 * (1 - $parameter3))) AS ?newRows2)
    BIND(?rows1 - ?newRows2 AS ?newRows1)
}
''',
        ),
    ],
)

top_absolute_train_test_split_component = Component(
    name='Top K Absolute Train-Test Split',
    implementation=partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(list(implementation_parameters.keys())[0], "Absolute"),
        ParameterSpecification(list(implementation_parameters.keys())[1], "First"),
    ],
    exposed_parameters=[
        list(implementation_parameters.keys())[3],
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(1, 2),
        Transformation(
            query='''
DELETE {
    $output1 dmop:numberOfRows ?rows1.
    $output2 dmop:numberOfRows ?rows1.
}
INSERT {
    $output1 dmop:numberOfRows ?newRows1 .
    $output1 dmop:isTrainDataset True .
    $output2 dmop:numberOfRows ?newRows2 .
    $output2 dmop:isTestDataset True .
}
WHERE {
    $output1 dmop:numberOfRows ?rows1.
    BIND(IF( ?rows1 - $parameter4>0, ?rows1 - $parameter4, 0 ) AS ?newRows2)
    BIND(?rows1 - ?newRows2 AS ?newRows1)
}
''',
        ),
    ],
)
