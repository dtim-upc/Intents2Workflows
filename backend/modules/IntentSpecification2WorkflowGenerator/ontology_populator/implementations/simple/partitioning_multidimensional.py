from common import *
from ..core import *

tensor_partitioning_implementation = Implementation(
    name='Tensor Data Partitioning',
    algorithm=cb.Partitioning,
    parameters=[
        Parameter("Partition method", XSD.string, None),
        Parameter("Sampling method", XSD.string, None),
        Parameter("Fraction (Relative size)", XSD.double, 0.8),
        Parameter("Count (Absolute size)", XSD.int, 100),
        Parameter("Random seed", XSD.string, None),
        Parameter("Class columns", XSD.string, None),
    ],
    input=[
        cb.TensorDataset,
    ],
    output=[
        cb.TrainTensorDatasetShape,
        cb.TestTensorDatasetShape,
    ],

)

implementation_parameters = tensor_partitioning_implementation.parameters

tensor_random_relative_train_test_split_component = Component(
    name='Random Relative Train-Test Split (Tensor)',
    implementation=tensor_partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Partition method'), None),"Relative"),
        ParameterSpecification(next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Sampling method'), None),"Random"),
    ],
    exposed_parameters=[
        next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Fraction (Relative size)'), None),
        next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Random seed'), None),
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TensorDataset, 'weight': 1}
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
    BIND(ROUND(?rows1 * (1 - $parameter3)) AS ?newRows1)
    BIND(?rows1 - ?newRows1 AS ?newRows2)
}
''',
        ),
    ],
)

tensor_random_absolute_train_test_split_component = Component(
    name='Random Absolute Train-Test Split (Tensor)',
    implementation=tensor_partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Partition method'), None),"Absolute"),
        ParameterSpecification(next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Sampling method'), None),"Random"),
    ],
    exposed_parameters=[
        next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Count (Absolute size)'), None),
        next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Random seed'), None),
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TensorDataset, 'weight': 1}
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
    BIND(IF( ?rows1 - $parameter4>0, ?rows1 - $parameter4, 0 ) AS ?newRows1)
    BIND(?rows1 - ?newRows1 AS ?newRows2)
}
''',
        ),
    ],
)

tensor_top_relative_train_test_split_component = Component(
    name='Top K Relative Train-Test Split (Tensor)',
    implementation=tensor_partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Partition method'), None),"Relative"),
        ParameterSpecification(next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Sampling method'), None),"First"),
    ],
    exposed_parameters=[
        next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Fraction (Relative size)'), None),
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TensorDataset, 'weight': 1}
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
    BIND(ROUND(?rows1 * (1 - $parameter3)) AS ?newRows1)
    BIND(?rows1 - ?newRows1 AS ?newRows2)
}
''',
        ),
    ],
)

tensor_top_absolute_train_test_split_component = Component(
    name='Top K Absolute Train-Test Split (Tensor)',
    implementation=tensor_partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Partition method'), None),"Absolute"),
        ParameterSpecification(next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Sampling method'), None),"First"),
    ],
    exposed_parameters=[
        next((param for param in tensor_partitioning_implementation.parameters.keys() if param.label == 'Count (Absolute size)'), None),
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TensorDataset, 'weight': 1}
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
    BIND(IF( ?rows1 - $parameter4>0, ?rows1 - $parameter4, 0 ) AS ?newRows1)
    BIND(?rows1 - ?newRows1 AS ?newRows2)
}
''',
        ),
    ],
)
