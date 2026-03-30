from pathlib import Path
import sys
import json
from rdflib.collection import Collection

from common import *
from implementations.core import Implementation, IOSpecTag, OutputIOSpec, InputIOSpec, Component

with open('./sklearn_miner.json') as f:
    sklearn_dict = json.load(f)

common_graph = Graph().parse("Perplexity/common_shapes.ttl", format="turtle")


def init_cbox() -> Graph:
    cbox = get_graph_xp()

    cbox.add((URIRef(str(cb)), RDF.type, OWL.Ontology))
    cbox.add((URIRef(str(cb)), RDFS.label, Literal("ExtremeXP Ontology CBox")))

    return cbox

def add_operations(cbox):
    operations = [
        cb.SUM,
        cb.SUB,
        cb.MUL,
        cb.DIV,
        cb.POW,
        cb.SQRT,
        cb.EQ,
        cb.NEQ,
        cb.COPY,
    ]

    for o in operations:
        cbox.add((o, RDF.type, tb.Operation))

def add_engines(cbox):
    engines = [
        cb.KNIME,
        cb.Python,
    ]

    for engine in engines:
        cbox.add((engine, RDF.type, tb.Engine))

problem_dict={
    "transformer": cb.DataTransformation,
    "classifier": cb.Classification,
    "cluster": cb.Clustering,
    "regressor": cb.Regression
}

def add_problems(cbox):
    problems = problem_dict.values()
    for p in problems:
        cbox.add((p, RDF.type, tb.Task))



def add_algorithm(cbox, algorithm_name, problem):
    algorithm = cb.term(algorithm_name)
    cbox.add((algorithm, RDF.type, tb.Algorithm))
    cbox.add((algorithm, RDFS.label, Literal(algorithm_name)))
    cbox.add((algorithm, tb.solves, problem))
    return algorithm

def get_shape_injected(shapePath: Path):
    shapeGraph = Graph().parse(shapePath)
    return shapeGraph




def getIOPorts(cbox:Graph, component, input_ports=True):
    port_type = "input" if input_ports else "output"
    ports = []
    for port in Path(component/port_type).iterdir():
        iotags = []
        for element in port.iterdir():
                
                if element.suffix == '.ttl':
                    shape = element
                    if (cb.term(shape.stem), RDF.type, SH.NodeShape) not in cbox:
                        print(cb.term(shape.stem), RDF.type, SH.NodeShape)
                        newshape = get_shape_injected(shape)
                        if not newshape is None:
                            cbox += newshape
       
                    iotags.append(IOSpecTag(cb.term(shape.stem)))
            
        ports.append(InputIOSpec(iotags)) if input_ports else ports.append(OutputIOSpec(iotags))
    return ports

def get_transformations(component):
    port_type = "output"
    transf = []
    for port in Path(component/port_type).iterdir():
        for element in port.iterdir():
            if element.suffix == '.sparql':
                transf.append(element.read_text())
    return transf




def add_components (cbox:Graph):
    sahpesPath = Path("./Perplexity/clean/")

    for component in sahpesPath.iterdir():
        print("Generant", component.name)

        
        inputs = getIOPorts(cbox, component, input_ports=True)
        outputs = getIOPorts(cbox, component, input_ports=False)


        component_type = sklearn_dict[component.name]["estimator_type"]
        problem = problem_dict[component_type]

        
        algorithm = add_algorithm(cbox, component.name, problem)
        implementation = Implementation(name=component.name, algorithm=algorithm, parameters=[], input=inputs, output = outputs, implementation_type=tb.LearnerImplementation, transformations = get_transformations(component))
        impl_component = Component(name=implementation.name+" Component", implementation=implementation, transformations=[])
        applier_implementation = Implementation(name=component.name+" Applier", algorithm=algorithm, parameters=[], input=inputs, output = outputs, 
                                                implementation_type=tb.ApplierImplementation, counterpart=implementation)
        appl_component = Component(name=component.name+" Applier Component", implementation=applier_implementation, transformations=[], counterpart=impl_component)
        
        implementation.add_to_graph(cbox)
        applier_implementation.add_to_graph(cbox)
        impl_component.add_to_graph(cbox)
        appl_component.add_to_graph(cbox)

        implementation.add_counterpart_relationship(cbox)
        applier_implementation.add_counterpart_relationship(cbox)
        impl_component.add_counterpart_relationship(cbox)
        appl_component.add_counterpart_relationship(cbox)

def add_partitioning(cbox:Graph):
    inputs = [InputIOSpec(io_tags=[])]
    outputs = [OutputIOSpec(io_tags=[IOSpecTag(cb.isTrainDatasetShapeDatasetShape)]), OutputIOSpec(io_tags=[IOSpecTag(cb.isTestDatasetShapeDatasetShape)])]

    algorithm = add_algorithm(cbox, "partition", cb.DataTransformation)
    implementation = Implementation("Data partition", algorithm, parameters=[], input=inputs, output=outputs)
    component = Component("Data partition component", implementation=implementation, transformations=[])

    implementation.add_to_graph(cbox)
    component.add_to_graph(cbox)

def add_sanitizer(cbox:Graph):
    inputs = [InputIOSpec(io_tags=[])]
    outputs = [OutputIOSpec(io_tags=[IOSpecTag(cb.isCategoricalOrNumericPropertyShapeFeatureShape)])]


    transformation_query = f""" 
    DELETE {{

    ?subject <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#hasDataPrimitiveTypeColumn> ?insVal_1 .
    
    }}
    INSERT {{

    ?subject <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#hasDataPrimitiveTypeColumn> <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#CategoricalOrNumeric> .
    
    }}
    WHERE {{
    ?base a dmop:TabularDataset .
    ?base dmop:hasColumn ?subject .
    OPTIONAL {{ ?subject <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#hasDataPrimitiveTypeColumn> ?insVal_1 . }}
    ?subject <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#isFeature> true.
    }}
    """

    algorithm = add_algorithm(cbox, "cleaning", cb.DataTransformation)
    implementation = Implementation("Nonstandard column remover", algorithm, parameters=[], input=inputs, output=outputs, transformations= [transformation_query])
    component = Component("Nonstandard column remover component", implementation=implementation, transformations=[])
        
    implementation.add_to_graph(cbox)
    component.add_to_graph(cbox)



def main(dest='./Ontology/cbox_deep.ttl'):
    cbox = init_cbox()
    add_operations(cbox)
    add_engines(cbox)
    add_problems(cbox)
    cbox += common_graph
    add_components(cbox)
    add_partitioning(cbox)
    add_sanitizer(cbox)


    #add_algorithms(cbox)
    #add_implementations(cbox)
    #add_models(cbox)
    #add_shapes(cbox)

    cbox.serialize(dest, format='turtle')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
