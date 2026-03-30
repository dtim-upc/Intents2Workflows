import json
from pathlib import Path
import jinja2
from rdflib import Graph, RDF, Literal, Namespace, URIRef
from base_shape import BaseShape, ConditionalShape
from common_shapes import BASE_SHAPES
from common import dmop

environment = jinja2.Environment(loader=jinja2.FileSystemLoader(["./"]))

def uri(value):
    return isinstance(value, URIRef)

environment.tests['uri'] = uri


def render_feature_shape(shape_name, base_shape):
    feature_shape_template = environment.get_template('feature_shape.ttl.jinja')
    feature_shape = feature_shape_template.render(shape_name = shape_name, base_shape = base_shape)
    return feature_shape
    
def render_label_shape(shape_name, base_shape):
    feature_shape_template = environment.get_template('label_shape.ttl.jinja')
    feature_shape = feature_shape_template.render(shape_name = shape_name, base_shape = base_shape)
    return feature_shape

def render_dataset_shape(shape_name, base_shape):
    feature_shape_template = environment.get_template('dataset_shape.ttl.jinja')
    feature_shape = feature_shape_template.render(shape_name = shape_name, base_shape = base_shape)
    return feature_shape

def render_model_shape(shape_name, target):
    feature_shape_template = environment.get_template('model_shape.ttl.jinja')
    feature_shape = feature_shape_template.render(shape_name = shape_name, target = target)
    return feature_shape

def render_transformation(insertions, dependences, conditions, columnar_type = True):
    transf_template = environment.get_template("transformation_query.sparql.jinja")
    transf = transf_template.render(insertions = insertions, dependences = dependences, conditions = conditions, columnarType = columnar_type)
    return transf


def open_file(file_path:Path):
    with open(file_path, mode='r') as f:
        file = f.read()
    return file

base_shape_dict = {s.name : s for s in BASE_SHAPES}|{"cb:"+s.name : s for s in BASE_SHAPES}

def render_shapes_from_io(io_port, spec_path):

    dependences = set()
    transformations = set()
    for feature in io_port["feature_properties"]:
        assert feature in base_shape_dict, f"Property {feature} not in common shapes"
        if feature.find('cb:') != -1:
            feature = feature[3:]
        print("feature", feature)
        rendered_shape = render_feature_shape(f"{feature}FeatureShape", feature)
        print("Guardant", spec_path /f"{feature}FeatureShape.ttl")
        with open( spec_path /f"{feature}FeatureShape.ttl", mode='w') as f:
            f.write(rendered_shape)
        
        bs = base_shape_dict[feature]
        transformations = transformations.union(bs.transformations) #we are assuming no contradiction here between transformations. 
        dependences = dependences.union(bs.dependences)
    
    feature_transformations = render_transformation(insertions=transformations, dependences=dependences.intersection([t[0] for t in transformations]), 
                                           conditions=[(dmop.isFeature, Literal(True))]) #ensure that if triple is defined using transformations does not appear as dependence

    dependences = set()
    transformations = set()
    for label in io_port["label_properties"]:
        assert label in base_shape_dict, f"Property {label} not in common shapes"
        if label.find('cb:') != -1:
            label = label[3:]
        print("label", label)
        rendered_shape = render_label_shape(f"{label}LabelShape", label)
        with open( spec_path /f"{label}LabelShape.ttl", mode='w') as f:
            f.write(rendered_shape)
        
        bs = base_shape_dict[label]
        transformations = transformations.union(bs.transformations) #we are assuming no contradiction here between transformations. 
        dependences = dependences.union(bs.dependences)

    label_transformations = render_transformation(insertions=transformations, dependences=dependences.intersection([t[0] for t in transformations]), 
                                           conditions=[(dmop.isLabel, Literal(True))]) 
            
    dependences = set()
    transformations = set()
    for data in io_port["dataset_properties"]:
        assert data in base_shape_dict, f"Property {data} not in common shapes"
        if data.find('cb:') != -1:
            data = data[3:]
        print("data",data)
        rendered_shape = render_dataset_shape(f"{data}DatasetShape", data)
        with open( spec_path /f"{data}DatasetShape.ttl", mode='w') as f:
            f.write(rendered_shape)
        
        bs = base_shape_dict[data]
        transformations = transformations.union(bs.transformations) #we are assuming no contradiction here between transformations. 
        dependences = dependences.union(bs.dependences)

    dataset_transformations = render_transformation(insertions=transformations, dependences=dependences.intersection([t[0] for t in transformations]), 
                                           conditions=[], columnar_type=False) 
    
    
    with open(spec_path /f"featureTransformations.sparql", mode='w') as f:
            f.write(feature_transformations)
    with open(spec_path /f"labelTransformations.sparql", mode='w') as f:
            f.write(label_transformations)
    with open(spec_path /f"datasetTransformations.sparql", mode='w') as f:
            f.write(dataset_transformations)

def main():
    gpt = Path('./Perplexity/components')
    gpt_out = Path('./Perplexity/clean')

    with open("./sklearn_miner.json") as f:
        raw = f.read()

    sklearn_components = json.loads(raw)

    with open('./Perplexity/common_shapes.ttl') as f:
        raw = f.read()


    for component in sklearn_components.values():
        print(f"####################### {component['name']} ###########################")

        if not component["needs_parameter_specification"] and component['name'] not in ['MissingIndicator']:
            component_path:Path = gpt / f"{component['name']}.json"
            component_out = gpt_out / component["name"]
            component_out.mkdir(exist_ok=True)
            component_inputs = component_out / "input"
            component_inputs.mkdir(exist_ok=True)
            component_outputs = component_out / "output"
            component_outputs.mkdir(exist_ok=True)

            with open(component_path) as f:
                component_json = json.load(f)[component["name"]]
            
            print(component_json["inputs"])

            for num,i in enumerate(component_json["inputs"]):
                spec_path = component_inputs / f"{num}"
                spec_path.mkdir(exist_ok=True)
                render_shapes_from_io(i, spec_path)

            if component["estimator_type"] == "transformer":
                print(component_json["data_outputs"])
                
                for num, o in enumerate(component_json["data_outputs"]):
                    spec_path = component_outputs / f"{num}"
                    spec_path.mkdir(exist_ok=True)
                    render_shapes_from_io(o, spec_path)

            else:
                print("No data outputs")
                num = 0

            if "model_output" in component_json:

                if component_json["model_output"] == {}:
                    model = "TransformerModel"
                else:
                    model = component_json["model_output"]["model_type"]

                print("model", model)

                spec_path = component_outputs / f"{len(component_json['data_outputs'])}"
                spec_path.mkdir(exist_ok=True)
                rendered_shape = render_model_shape(f"{model}", model)
                with open( spec_path /f"{model}ModelShape.ttl", mode='w') as f:
                    f.write(rendered_shape)

                    
        else:
            print("Component no materialitzat per paràmetre obligatori")

main()