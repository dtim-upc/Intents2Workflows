from pathlib import Path
import sys, os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common import *
from implementations.core import Implementation, IOSpecTag, OutputIOSpec, InputIOSpec, Component, Parameter, AbstractImplementation, FactorParameter
from implementations.python.python_implementation import PythonImplementation
from implementations.python.python_parameter import PythonTextParameter, PythonFactorParameter, PythonNumericParameter
from implementations.python.io import python_reader_implementation, python_writer_implementation
from implementations.simple.io import data_reader_implementation, data_reader_components, data_writer_implementation, data_writer_component
from implementations.core.expression import AlgebraicExpression


with open('./auto_populator/sklearn_miner.json') as f:
    sklearn_dict = json.load(f)

sklearn_dict['SimpleImputerGeneric'] = sklearn_dict["SimpleImputer"]
#sklearn_dict['SimpleImputerGeneric']['name'] = 'SklearnImputer'

common_graph = Graph().parse("./auto_populator/Perplexity/common_shapes.ttl", format="turtle")
  
custom_parameters = {}
custom_parameters['SimpleImputerGeneric'] = [
    FactorParameter("strategy", levels=["most_frequent", "constant"], default_value="most_frequent")
]
  
custom_python_parameters = {}
custom_python_parameters['SimpleImputerGeneric'] = [
    PythonFactorParameter("strategy", levels={"most_frequent": "most_frequent", "constant":"constant"}, 
                          base_parameter= next((param for param in custom_parameters['SimpleImputerGeneric'] if param.label == 'strategy'),None),
                          default_value="most_frequent")
]
custom_python_parameters['OneHotEncoder'] = [
    PythonNumericParameter("sparse_output",datatype=XSD.boolean, expression=AlgebraicExpression(cb.COPY, False), default_value=False)
]


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
    model_ports = []
    is_model_port = False
    for port in Path(component/port_type).iterdir():
        iotags = []
        for element in port.iterdir(): 
                
                if element.suffix == '.ttl':
                    shape = element
                    if (cb.term(shape.stem), RDF.type, SH.NodeShape) not in cbox:
                        #print(cb.term(shape.stem), RDF.type, SH.NodeShape)
                        newshape = get_shape_injected(shape)
                        if not newshape is None:
                            cbox += newshape
 
                    iotags.append(IOSpecTag(cb.term(shape.stem)))
                    if (cb.term(shape.stem), RDF.type, tb.ModelTag) in cbox: 
                        is_model_port = True #on coincidence is enough to consider a port of model type    
                           
        if is_model_port:
            model_ports.append(InputIOSpec(iotags)) if input_ports else model_ports.append(OutputIOSpec(iotags))
            is_model_port=False
        else:
            ports.append(InputIOSpec(iotags)) if input_ports else ports.append(OutputIOSpec(iotags))
            
    return ports, model_ports

def get_transformations(component):
    port_type = "output"
    transf = []
    for port in Path(component/port_type).iterdir():
        for element in port.iterdir():
            if element.suffix == '.sparql':
                transf.append(element.read_text())
    return transf




def add_components (cbox:Graph):
    sahpesPath = Path("./auto_populator/Perplexity/clean/")
    manual_path = Path("./auto_populator/manual/")
    abstract_impls = {}

    for iterator in (sahpesPath.iterdir(), manual_path.iterdir()):
        for component in iterator:
            print("Generant", component.name)

            component_type = sklearn_dict[component.name]["estimator_type"]
            problem = problem_dict[component_type]
            needs_applier = True #component_type in ["classifier", "regressor"]
            is_transformer = component_type == 'transformer'
            module = sklearn_dict[component.name]["module"]
            function = sklearn_dict[component.name]["name"]

            
            inputs, model_inputs = getIOPorts(cbox, component, input_ports=True)
            outputs, model_outputs = getIOPorts(cbox, component, input_ports=False)

            implementation_type= tb.LearnerImplementation if needs_applier  else tb.Implementation


            algorithm = add_algorithm(cbox, component.name, problem)
            implementation = Implementation(name=component.name, algorithm=algorithm, parameters=[
                Parameter("Target Class column", XSD.string, default_value="$$LABEL_CATEGORICAL$$"),
                *custom_parameters.get(component.name, [])
            ], 
            input=inputs, output = model_outputs + outputs if needs_applier else outputs, implementation_type=implementation_type, transformations = get_transformations(component))
            impl_component = Component(name=implementation.name+" Component", implementation=implementation, transformations=[])
            
            implementation.add_to_graph(cbox)
            impl_component.add_to_graph(cbox)

            #Dict for generating abstract implementations by grouping implementations with the same input and output data specs
            for output in outputs:
                key =frozenset([frozenset([hash(i) for i in inputs]),hash(output)])
                if key in abstract_impls:
                    abstract_impls[key]['implementations'].append(implementation)
                else:
                    abstract_impls[key] = {
                        'implementations':[implementation],
                        'output': [output]
                    }

            if needs_applier:
                if is_transformer:
                    python_template = 'sklearn_train_transform'
                else:
                    python_template = "sklearn_train"
            else:
                python_template = "basic_sklearn_fittransform_function"


            python_impl = PythonImplementation(name=f"{component.name}Python", baseImplementation=implementation, parameters=[
                    PythonTextParameter(key="Target", 
                                        base_parameter= next((param for param in implementation.parameters.keys() if param.label == 'Target Class column'),None),
                                        default_value="target", control_parameter=True),
                    *custom_python_parameters.get(component.name, [])
            ],python_module=f'sklearn.{module}', python_dependences=[('scikit-learn', '1.7.2')], python_function=function, template=python_template)
            python_impl.add_to_graph(cbox)


            if needs_applier:
                applier_model_inputs = [InputIOSpec(m.specs) for m in model_outputs] 
                applier_data_inputs = inputs
                #for i in applier_data_inputs:
                #    i.specs.append(IOSpecTag(cb.isTestDatasetShapeDatasetShape))
                applier_implementation = Implementation(name=component.name+" Applier", algorithm=algorithm, parameters=[], input=applier_model_inputs+applier_data_inputs, 
                                                        output = outputs if is_transformer else [OutputIOSpec([IOSpecTag(cb.isTabularDatasetShapeDatasetShape)])], 
                                                        implementation_type=tb.ApplierImplementation, counterpart=implementation)
                appl_component = Component(name=component.name+" Applier Component", implementation=applier_implementation, transformations=[], counterpart=impl_component) 
                
                
                applier_implementation.add_to_graph(cbox) 
                appl_component.add_to_graph(cbox)
                implementation.add_counterpart_relationship(cbox)
                applier_implementation.add_counterpart_relationship(cbox)
                impl_component.add_counterpart_relationship(cbox)
                appl_component.add_counterpart_relationship(cbox)

                if is_transformer:
                    applier_template = 'sklearn_test_transform'
                else:
                    applier_template = 'sklearn_predict'

                python_impl = PythonImplementation(name=f"{component.name}TestPython", baseImplementation=applier_implementation, parameters=[],
                                                python_module='sklearn', python_dependences=[('scikit-learn', '1.7.2')], python_function=function, template=applier_template)
                python_impl.add_to_graph(cbox)

        #Generate abstract implementations
        for key, values in abstract_impls.items():
        
            implementations = values['implementations']
            assert len(implementations) > 0
            impl:Implementation = implementations[0]
            inputs = impl.input
            print(inputs)
            outputs = values['output']
            name = str(hash(key))+ "_" + impl.name + " Aggregation"
            abs = AbstractImplementation(name=name,implementations=implementations, input=inputs, output=outputs)
            abs.add_to_graph(cbox)

 
def add_partitioning(cbox:Graph):
    inputs = [InputIOSpec(io_tags=[IOSpecTag(cb.isTabularDatasetShapeDatasetShape)])]
    outputs = [OutputIOSpec(io_tags=[IOSpecTag(cb.isTrainDatasetShapeDatasetShape)]), OutputIOSpec(io_tags=[IOSpecTag(cb.isTestDatasetShapeDatasetShape)])]

    algorithm = add_algorithm(cbox, "partition", cb.DataTransformation) 
    implementation = Implementation("Data partition", algorithm, parameters=[], input=inputs, output=outputs)
    abs_implementation = AbstractImplementation("Data partitioners", implementations=[implementation], input=implementation.input, output=implementation.output)
    component = Component("Data partition component", implementation=implementation, transformations=[])

    implementation.add_to_graph(cbox) 
    component.add_to_graph(cbox)

    abs_implementation.add_to_graph(cbox)



    python_impl = PythonImplementation(name=f"PartitioningPython", baseImplementation=implementation, parameters=[],
                                        python_module='sklearn.model_selection', python_dependences=[('scikit-learn', '1.7.2')], python_function='train_test_split',
                                        template='basic_function')
    python_impl.add_to_graph(cbox)

    cbox.add((cb.isTrainDatasetShapeDatasetShape, RDF.type, sh.NodeShape))
    cbox.add((cb.isTrainDatasetShapeDatasetShape, sh.property, cb.isTrainDatasetShape))
    cbox.add((cb.isTrainDatasetShapeDatasetShape, sh.targetClass, dmop.TabularDataset))

    cbox.add((cb.isTestDatasetShapeDatasetShape, RDF.type, sh.NodeShape))
    cbox.add((cb.isTestDatasetShapeDatasetShape, sh.property, cb.isTestDatasetShape))
    cbox.add((cb.isTestDatasetShapeDatasetShape, sh.targetClass, dmop.TabularDataset))


def add_sanitizer(cbox:Graph):
    inputs = [InputIOSpec(io_tags=[IOSpecTag(cb.isTabularDatasetShapeDatasetShape)])]
    outputs = [OutputIOSpec(io_tags=[IOSpecTag(cb.isCategoricalOrNumericPropertyShapeFeatureShape)])]


    transformation_query = f""" 
    DELETE {{

    ?subject ?predicate ?object .
    ?base dmop:hasColumn ?subject .
    
    }}
    WHERE {{
    ?base a dmop:TabularDataset .
    ?base dmop:hasColumn ?subject .
    VALUES ?subject {{ $$COLUMNS_TO_TRANSFORM$$ }}
    OPTIONAL {{ ?subject <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#hasDataPrimitiveTypeColumn> ?insVal_1 . }}
    ?subject <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#isFeature> true.
    }}
    """

    algorithm = add_algorithm(cbox, "cleaning", cb.DataTransformation)
    implementation = Implementation("Nonstandard column remover", algorithm, parameters=[], input=inputs, output=outputs, transformations= [transformation_query])
    abs_implementation = AbstractImplementation("Column removers", implementations=[implementation], input=implementation.input, output=implementation.output)
    component = Component("Nonstandard column remover component", implementation=implementation, transformations=[])
        
    implementation.add_to_graph(cbox)
    component.add_to_graph(cbox)

    abs_implementation.add_to_graph(cbox)

    python_impl = PythonImplementation(name=f"ColumnRemoverPython", baseImplementation=implementation, parameters=[],
                                        python_module='pandas', python_dependences=[('pandas', '3.0.2')], python_function='',
                                        template='column_remover')
    python_impl.add_to_graph(cbox)



def add_io(cbox:Graph):
    data_reader_implementation.add_to_graph(cbox)

    for reader in data_reader_components:
        reader.add_to_graph(cbox)

    data_writer_implementation.add_to_graph(cbox)
    data_writer_component.add_to_graph(cbox)

    python_reader_implementation.add_to_graph(cbox)
    python_writer_implementation.add_to_graph(cbox)
    

def add_datasets(cbox):
    cbox.add((dmop.TabularDataset, RDF.type, tb.Dataset))

    cbox.add((dmop.TensorDataset, RDF.type, tb.Dataset))

    cbox.add((dmop.Column, RDF.type, tb.Column))



def main(dest='../ontologies/cbox_deep.ttl'):
    cbox = init_cbox()
    add_operations(cbox)
    add_engines(cbox)
    add_problems(cbox)
    cbox += common_graph
    add_components(cbox)
    add_partitioning(cbox)
    add_sanitizer(cbox)
    add_io(cbox)
    add_datasets(cbox)


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
