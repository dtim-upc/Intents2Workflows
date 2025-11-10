from common import *
from ..core.implementation import Implementation
from ..core.parameter import Parameter
from ..core.component import Component
from ..core.transformation import *
from ..core.iospec import InputIOSpec, OutputIOSpec, IOSpecTag


dbscan_implementation = Implementation(
    name="DBSCAN",
    algorithm=cb.DBSCAN,
    parameters= [
        Parameter("epsilon", XSD.float),
        Parameter("minimum samples", XSD.int)
    ],
    input = [
        InputIOSpec([IOSpecTag(cb.TabularDatasetShape)]),
        
    ],
    output=[
        OutputIOSpec([IOSpecTag(cb.TabularDatasetShape)]),
    ],
) 

dbscan_component = Component(
    name="DBSCAN component",
    implementation=dbscan_implementation,
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query='''
INSERT {
    $output1 dmop:hasColumn _:labelColumn .
    _:labelColumn a dmop:Column ;
        dmop:isLabel true;
      dmop:hasName $parameter1.
}
WHERE {
    $input1 cb:setsClassColumnName ?classColumnName .
}
            ''',
        ),
    ],
    exposed_parameters=[],
    overriden_parameters=[],
)