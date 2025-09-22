from common import *
from ontology_populator.implementations.core import *

FORMATS = ["CSV", "Parquet", "ZIP", "Folder", "NumpyZip"] #TODO automatically get this list
data_reader_implementation = Implementation(
    name='Data Reader',
    algorithm=cb.DataLoading,
    parameters=[
        Parameter("Reader File", XSD.string, '$$PATH$$'),
        Parameter("Format", XSD.string, '$$DATA_RAW_FORMAT$$')
    ],
    input=[],
    output=[
        cb.TabularDataset,
    ],
)

data_reader_components = []

for format in FORMATS:
    component = Component(
        name=f"{format} Reader component",
        implementation=data_reader_implementation,
        transformations=[LoaderTransformation()],
        overriden_parameters=[
            ParameterSpecification(next((param for param in data_reader_implementation.parameters.keys() if param.label == 'Format'), None), format)
        ],
        exposed_parameters=[
            next((param for param in data_reader_implementation.parameters.keys() if param.label == 'Reader File'), None)
        ],
    )
    data_reader_components.append(component)

data_writer_implementation = Implementation(
    name='Data Writer',
    algorithm=cb.DataStoring,
    parameters=[
        Parameter('Output path', XSD.string, r"./output.csv"),
    ],
    input=[cb.TabularDatasetShape],
    output=[],
)

data_writer_component = Component(
    name='Data Writer component',
    implementation=data_writer_implementation,
    transformations=[],
    overriden_parameters=[
    ],
    exposed_parameters=[
    ]

)