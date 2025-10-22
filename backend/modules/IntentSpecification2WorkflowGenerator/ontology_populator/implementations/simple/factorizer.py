from ..core import *
from common import *

columns_parameter = Parameter("Columns to factorize", datatype=XSD.string, default_value="$$CATEGORICAL_COLUMNS$$")

factorizer_implemenation = Implementation(
    name = "Factorizer",
    algorithm=cb.DataManagement,
    parameters = [
        columns_parameter,
    ],
    input=[
        InputIOSpec([IOSpecTag(cb.TabularDataset)]),
    ],
    output=[
        OutputIOSpec([IOSpecTag(cb.NumericCategoricalTabularDatasetShape)]),
        OutputIOSpec([IOSpecTag(cb.NumericCategoricalModel)]),
    ],
    implementation_type=tb.LearnerImplementation,
)

factorizer_component = Component(
    name="Factorizer component",
    implementation=factorizer_implemenation,
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query='''
DELETE {
  ?column dmop:hasDataPrimitiveTypeColumn ?oldDatatype .
}
INSERT {
  ?column dmop:hasDataPrimitiveTypeColumn xsd:int . 
}
WHERE {
  $output2 dmop:hasColumn ?column .
  ?column dmop:isCategorical true .
  ?column dmop:datatype ?oldDatatype . 
}
''',
        ),
    ],
)

factorizer_applier_output_spec_data =  OutputIOSpec([IOSpecTag(cb.NumericCategoricalTabularDatasetShape)])

factorizer_applier_implementation = Implementation(
    name='Factorizer (Applier)',
    algorithm=cb.DataManagement,
    parameters=[
        columns_parameter,
    ],
    input=[
        InputIOSpec([IOSpecTag(cb.NumericCategoricalModel)]),
        InputIOSpec([IOSpecTag(cb.TestTabularDatasetShape)])
    ],
    output=[
       factorizer_applier_output_spec_data
    ],
    implementation_type=tb.ApplierImplementation,
)

#TODO add one-hot encoder?

factorizer_applier_component = Component(
    name='Factorizer Applier Component',
    implementation=factorizer_applier_implementation,
    overriden_parameters=[],
    exposed_parameters=[],
    transformations=[
        CopyTransformation(2, 1),
        Transformation(
            query='''
DELETE {
  ?column dmop:hasDataPrimitiveTypeColumn ?oldDatatype .
}
INSERT {
  ?column dmop:hasDataPrimitiveTypeColumn xsd:int . 
}
WHERE {
  $output2 dmop:hasColumn ?column .
  ?column dmop:isCategorical true .
  ?column dmop:datatype ?oldDatatype . 
}
''',
        ),
    ],
    counterpart=[
        factorizer_component
    ]
)
