import json
from pathlib import Path
import jinja2
from rdflib import Literal, URIRef, RDF, Graph
import os, sys

root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

from common_shapes import BASE_SHAPES
from common import dmop, tb, cb, get_graph_xp
from graph_queries.shape_queries import get_nodes_that_satisfy_shape

environment = jinja2.Environment(loader=jinja2.FileSystemLoader(["./"]))

def uri(value):
    return isinstance(value, URIRef)

environment.tests['uri'] = uri


def render_feature_shape(shape_name, base_shape, subshapes):
    feature_shape_template = environment.get_template('feature_shape.ttl.jinja')
    feature_shape = feature_shape_template.render(shape_name = shape_name, base_shape = base_shape, subshapes = subshapes)
    return feature_shape
    
def render_label_shape(shape_name, base_shape, subshapes):
    feature_shape_template = environment.get_template('label_shape.ttl.jinja')
    feature_shape = feature_shape_template.render(shape_name = shape_name, base_shape = base_shape, subshapes = subshapes)
    return feature_shape

def render_dataset_shape(shape_name, base_shape, subshapes):
    feature_shape_template = environment.get_template('dataset_shape.ttl.jinja')
    feature_shape = feature_shape_template.render(shape_name = shape_name, base_shape = base_shape, subshapes = subshapes)
    return feature_shape

def render_model_shape(shape_name, target):
    feature_shape_template = environment.get_template('model_shape.ttl.jinja')
    feature_shape = feature_shape_template.render(shape_name = shape_name, target = target)
    return feature_shape

def render_transformation(insertions, dependences, conditions, columnar_type = True):
    if len(insertions) <= 0:
        return None
    
    transf_template = environment.get_template("transformation_query.sparql.jinja")
    transf = transf_template.render(insertions = insertions, dependences = dependences, conditions = conditions, columnarType = columnar_type)
    return transf


def open_file(file_path:Path):
    with open(file_path, mode='r') as f:
        file = f.read()
    return file

base_shape_dict = {s.name : s for s in BASE_SHAPES}|{"cb:"+s.name : s for s in BASE_SHAPES}


def add_shapes_hierarchy():
    common_graph = Graph().parse("./auto_populator/Perplexity/common_shapes.ttl", format="turtle")
    subshapes = {}
    
    for b in BASE_SHAPES:
        is_columnar = b.type=="columnar" 
        query = render_transformation(b.transformations, b.dependences, conditions=[], columnar_type=is_columnar)
        

        g = get_graph_xp()
        dataset = cb[b.name+"Dataset"]

        g.add((dataset, RDF.type, dmop.TabularDataset))

        if is_columnar:
            g.add((dataset, dmop.hasColumn, cb.column))
            query = query.replace("$$COLUMNS_TO_TRANSFORM$$", "cb:column")
        
        keyf = f"{b.name}FeatureShape"
        keyl = f"{b.name}LabelShape"
        keyd = f"{b.name}DatasetShape"  
        
        print(query)

        if is_columnar:
            subshapes[keyf] = []
            subshapes[keyl] = []
        else:
            subshapes[keyd] = []

        if not query is None:
            g.update(query)
            #print(g.serialize())

            for b2 in BASE_SHAPES:
                if len(get_nodes_that_satisfy_shape(g,common_graph,cb[b2.name],[dataset] if b2.type !="columnar" else [cb.column])) > 0:
                    #print(b.name, "also satisfies", b2.name)

                    if is_columnar:
                        if b2.type == "columnar":
                            subshapes[keyf].append(f"{b2.name}FeatureShape")
                            subshapes[keyl].append(f"{b2.name}LabelShape")
                        else:
                            subshapes[keyf].append(f"{b2.name}DatasetShape")
                            subshapes[keyl].append(f"{b2.name}DatasetShape")
                    
                    else:
                        if b2.type == "columnar":
                            subshapes[keyd].append(f"{b2.name}FeatureShape")
                            subshapes[keyd].append(f"{b2.name}LabelShape")
                        else:
                            subshapes[keyd].append(f"{b2.name}DatasetShape")
    return subshapes
    

SUBSHAPES = add_shapes_hierarchy()



def render_shapes_from_io(io_port, spec_path):

    dependences = set()
    transformations = set()
    for feature in io_port["feature_properties"]:
        assert feature in base_shape_dict, f"Property {feature} not in common shapes"
        if feature.find('cb:') != -1:
            feature = feature[3:]

        feature_name = f"{feature}FeatureShape"

        subshapes = SUBSHAPES[feature_name]

        print("feature", feature)
        rendered_shape = render_feature_shape(feature_name, feature, subshapes)
        print("Guardant", spec_path /f"{feature_name}.ttl")
        with open( spec_path /f"{feature_name}.ttl", mode='w') as f:
            f.write(rendered_shape)
        
        bs = base_shape_dict[feature]
        transformations = transformations.union(bs.transformations) #we are assuming no contradiction here between transformations. 
        dependences = dependences.union(bs.dependences)

    feature_transformations = render_transformation(insertions=transformations, dependences=dependences.difference([t[0] for t in transformations]), 
                                            conditions=[(dmop.isFeature, Literal(True))]) #ensure that if triple is defined using transformations does not appear as dependence

    dependences = set()
    transformations = set()
    for label in io_port["label_properties"]:
        assert label in base_shape_dict, f"Property {label} not in common shapes"
        if label.find('cb:') != -1:
            label = label[3:]
        print("label", label)
        label_name = f"{label}LabelShape" 
        subshapes = SUBSHAPES[label_name]
        rendered_shape = render_label_shape(f"{label_name}", label, subshapes)
        with open( spec_path /f"{label_name}.ttl", mode='w') as f:
            f.write(rendered_shape)
        
        bs = base_shape_dict[label]
        transformations = transformations.union(bs.transformations) #we are assuming no contradiction here between transformations. 
        dependences = dependences.union(bs.dependences)

    label_transformations = render_transformation(insertions=transformations, dependences=dependences.difference([t[0] for t in transformations]), 
                                            conditions=[(dmop.isLabel, Literal(True))]) 
            
    dependences = set() 
    transformations = set()
    for data in io_port["dataset_properties"]:
        assert data in base_shape_dict, f"Property {data} not in common shapes"
        if data.find('cb:') != -1:
            data = data[3:]
        print("data",data)
        data_name = f"{data}DatasetShape"
        subshapes = SUBSHAPES.get(data_name,[])
        rendered_shape = render_dataset_shape(data_name, data, subshapes)
        with open( spec_path /f"{data_name}.ttl", mode='w') as f:
            f.write(rendered_shape)
        
        bs = base_shape_dict[data]
        transformations = transformations.union(bs.transformations) #we are assuming no contradiction here between transformations. 
        dependences = dependences.union(bs.dependences)

    dataset_transformations = render_transformation(insertions=transformations, dependences=dependences.difference([t[0] for t in transformations]), 
                                            conditions=[], columnar_type=False) 
    
    
    if feature_transformations is not None:
        with open(spec_path /f"featureTransformations.sparql", mode='w') as f:
                f.write(feature_transformations)
    if label_transformations is not None:
        with open(spec_path /f"labelTransformations.sparql", mode='w') as f:
                f.write(label_transformations)
    if dataset_transformations is not None:
        with open(spec_path /f"datasetTransformations.sparql", mode='w') as f:
                f.write(dataset_transformations)

def main():
    gpt = Path('./Perplexity/components')
    gpt_out = Path('./Perplexity/clean')

    with open("./sklearn_miner.json") as f:
        raw = f.read()

    sklearn_components = json.loads(raw)


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

            if "model_output" in component_json and component["estimator_type"] not in ["cluster"]: 

                if component_json["model_output"] == {}: 
                    model = "TransformerModel"
                else:
                    model = component_json["model_output"]["model_type"]

                print("model", model)

                spec_path = component_outputs / f"{len(component_json['data_outputs'])}"
                spec_path.mkdir(exist_ok=True)
                rendered_shape = render_model_shape(f"{model}ModelShape", model)
                with open( spec_path /f"{model}ModelShape.ttl", mode='w') as f:
                    f.write(rendered_shape)

                    
        else:
            print("Component no materialitzat per paràmetre obligatori")

main()