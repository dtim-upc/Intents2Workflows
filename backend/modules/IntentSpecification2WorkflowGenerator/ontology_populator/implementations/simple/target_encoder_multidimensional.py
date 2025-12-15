from ..core import *
from common import *

encoder_implemenation = Implementation(
    name = "Target encoder (tensor)",
    algorithm=cb.TargetEncoding,
    parameters = [
    ],
    input=[
        InputIOSpec([IOSpecTag(cb.TensorDatasetShape)]),
    ],
    output=[
        OutputIOSpec([IOSpecTag(cb.IntegerTargetTensorShape)]),
        OutputIOSpec([IOSpecTag(cb.EncoderModelShape)]),
    ],
    implementation_type=tb.LearnerImplementation,
)

encoder_component = Component(
    name="Encoder component",
    implementation=encoder_implemenation,
    transformations=[
    ],
)


encoder_applier_implementation = Implementation(
    name='Target encoder applier (tensor)',
    algorithm=cb.TargetEncoding,
    parameters=[
    ],
    input=[
        InputIOSpec([IOSpecTag(cb.EncoderModelShape)]),
        InputIOSpec([IOSpecTag(cb.TestTensorDatasetShape)])
    ],
    output=[
       OutputIOSpec([IOSpecTag(cb.IntegerTargetTensorShape)]),
    ],
    implementation_type=tb.ApplierImplementation,
)


encoder_applier_component = Component(
    name='Target encoder applier (tensor) Component',
    implementation=encoder_applier_implementation,
    overriden_parameters=[],
    exposed_parameters=[],
    transformations=[],
    counterpart=[
        encoder_component
    ]
)
