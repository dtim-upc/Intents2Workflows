from common import *
from .knime_implementation import KnimeBaseBundle, KnimeParameter, KnimeImplementation, KnimeDefaultFeature
from ..core import *

partitioning_implementation = KnimeImplementation(
    name='Data Partitioning',
    algorithm=cb.Partitioning,
    parameters=[
        KnimeParameter("Size type", XSD.string, None, "method"),
        KnimeParameter("Sampling Method", XSD.string, None, "samplingMethod"),
        KnimeParameter("Fraction (Relative size)", XSD.double, 0.8, "fraction"),
        KnimeParameter("Count (Absolute size)", XSD.int, 100, "count"),
        KnimeParameter("Random seed", XSD.string, None, "random_seed"),
        KnimeParameter("Class columns", XSD.string, None, "class_column"),
    ],
    input=[
        cb.TabularDataset,
    ],
    output=[
        cb.TrainTabularDatasetShape,
        cb.TestTabularDatasetShape,
    ],
    knime_node_factory='org.knime.base.node.preproc.partition.PartitionNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
)