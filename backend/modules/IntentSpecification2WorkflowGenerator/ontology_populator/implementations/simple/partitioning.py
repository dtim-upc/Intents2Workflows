from common import *
from ..core import *

partitioning_implementation = Implementation(
    name='Data Partitioning',
    algorithm=cb.Partitioning,
    parameters=[
        BaseFactorParameter("Size type", ['Absolute', 'Relative']),
        BaseFactorParameter("Sampling Method", ['Random', 'First']),
        BaseParameter("Fraction (Relative size)", XSD.double),
        BaseParameter("Count (Absolute size)", XSD.int),
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