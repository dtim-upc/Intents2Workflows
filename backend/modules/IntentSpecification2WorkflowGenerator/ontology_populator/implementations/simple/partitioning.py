from common import *
from ..core import *

partitioning_implementation = Implementation(
    name='Data Partitioning',
    algorithm=cb.Partitioning,
    parameters=[
        BaseFactorParameter("Size type", ['Absolute', 'Relative']),
        BaseFactorParameter("Sampling Method", ['Random', 'First']),
        BaseParameter("Fraction (Relative size)", XSD.double, 0.25),
        BaseParameter("Count (Absolute size)", XSD.int, 10),
        BaseParameter("Random seed", XSD.string),
        BaseParameter("Class columns", XSD.string),
    ],
    input=[
        cb.TabularDataset,
    ],
    output=[
        cb.TrainTabularDatasetShape,
        cb.TestTabularDatasetShape,
    ],
)