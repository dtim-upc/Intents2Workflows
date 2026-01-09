from common import *
from ontology_populator.implementations.core import *

FORMATS = ["ZIP", "Folder", "NumpyZip"] #TODO automatically get this list
tensor_data_reader_implementation = Implementation(
    name='Tensor Data Reader',
    algorithm=cb.DataLoading,
    parameters=[
        Parameter("Reader File", XSD.string, '$$PATH$$'),
        FactorParameter("Format", levels=FORMATS,  default_value = '$$DATA_RAW_FORMAT$$')
    ],
    input=[
        InputIOSpec([IOSpecTag(cb.UnsatisfiableShape)]), 
    ],
    output=[
        OutputIOSpec([IOSpecTag(cb.TensorDatasetShape)]),
    ],
)

tensor_data_reader_components = []

for format in FORMATS:
    component = Component(
        name=f"{format} Reader component (tensor)",
        implementation=tensor_data_reader_implementation,
        transformations=[LoaderTransformation()],
        overriden_parameters=[
            ParameterSpecification(next((param for param in tensor_data_reader_implementation.parameters.keys() if param.label == 'Format'), None), format)
        ],
        exposed_parameters=[
            next((param for param in tensor_data_reader_implementation.parameters.keys() if param.label == 'Reader File'), None)
        ],
    )
    tensor_data_reader_components.append(component)

tensor_data_writer_implementation = Implementation(
    name='Tensoor Data Writer',
    algorithm=cb.DataStoring,
    parameters=[
        Parameter('Output path', XSD.string, r"./output.csv"),
    ],
    input=[InputIOSpec([IOSpecTag(cb.TensorDataset)])],
    output=[],
)

tensor_data_writer_component = Component(
    name='Data Writer component (tensor)',
    implementation=tensor_data_writer_implementation,
    transformations=[],
    overriden_parameters=[
    ],
    exposed_parameters=[
    ]

)