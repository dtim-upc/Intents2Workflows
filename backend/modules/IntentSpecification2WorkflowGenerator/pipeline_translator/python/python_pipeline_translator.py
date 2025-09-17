import os
import sys
import tempfile
import zipfile
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Tuple, Dict, List
import jinja2
import math

from tqdm import tqdm

translator_dir = os.path.join(os.path.abspath(os.path.join('..')))
sys.path.append(translator_dir)

root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

environment = jinja2.Environment(loader=jinja2.FileSystemLoader(["pipeline_translator/python/templates", "templates"])) #the double path ensures expected performance on terminal and api execution
from pipeline_translator.core.translator_common_functions import *

from rdflib import Graph, URIRef, RDF, XSD


try:
    import easygui # type: ignore
except ImportError:
    easygui = None


def translate_factor_params(ontology:URIRef, workflow_graph: Graph, implementation:URIRef, step_parameters: Dict[URIRef,Literal]):
    python_params = []
    factor_params = get_engine_factor_params(ontology,implementation,engine='Python')
    print("python factor params:",factor_params)
    for param in factor_params:
        base_param = get_base_param(ontology, param)
        print(param,"base's param ->",base_param)
        if base_param in step_parameters.keys():
            value = translate_factor_level(ontology, base_param, step_parameters[base_param], param)
        else:
            value = get_default_value(ontology, param)

        key = next(ontology.objects(param, tb.python_key, unique=True))
        python_params.append((key, extract_literal_value(value)))
    return python_params


def calculate(term1, term2, operation):
    if term1 is None or (term2 is None and operation != "SQRT"):
        return None

    if operation == "SUM":
        return term1 + term2
    elif operation == "SUB":
        return term1 - term2
    elif operation == "MUL":
        return term1 * term2
    elif operation == "DIV":
        return term1 / term2
    elif operation == "POW":
        return term1 ^ term2 
    elif operation == "SQRT":
        return math.sqrt(term1)
    else:
        raise Exception("Invalid operation: "+operation)


def compute_algebraic_expression(ontology: Graph, expression: URIRef, step_parameters:URIRef):
    term1, term2, operation = unpack_expression(ontology,expression)

    assert not term1 is None and not operation is None

    operation = URIRef(operation).fragment
    assert (term2 is None and operation == 'SQRT') or not term2 is None

    print(term1, term2, operation)


    def compute_term_value(term):
        type = get_term_type(ontology, term)
        
        if type == "Parameter":
            if term in step_parameters.keys():
                value = step_parameters[term]
            else:
                print("Term",term,"not present in step parameters. Using default value")
                value= None
        elif type in ["integer", "decimal", "number"]:
                value = term
        elif type == "Expression":
                value = compute_algebraic_expression(ontology, term, step_parameters)
        else:
            raise Exception("Invalid term type: "+type)
        return value
    
    value_1 = compute_term_value(term1)
    value_2 = compute_term_value(term2) if not term2 is None else None

    return calculate(value_1, value_2, operation)

def translate_numeric_params(ontology:Graph, workflow_graph: Graph, implementation:URIRef, step_parameters: Dict[URIRef,Literal]):
    python_params = []
    numeric_params = get_engine_numeric_params(ontology,implementation,'Python')
    for param in numeric_params:
        alg_expression = get_algebraic_expression(ontology, param)
        value = compute_algebraic_expression(ontology, alg_expression, step_parameters)
        if value is None:
            value = get_default_value(ontology, param)
            print("Default value de",param,"és",value)
        
        key = next(ontology.objects(param, tb.python_key, unique=True))
        python_params.append((key, extract_literal_value(value)))
    return python_params

def get_step_parameters_agnostic(ontology: Graph, workflow_graph: Graph, step: URIRef) -> List[Tuple[str, str, str, URIRef]]:

    #print(f'STEP: {step}')
    parameters = list(workflow_graph.objects(step, tb.usesParameter, True))

    step_parameters = {}

    for param in parameters:
        spec = next(workflow_graph.objects(param, tb.specifiedBy, True))
        value = next(workflow_graph.objects(spec, tb.hasValue, True))
        step_parameters[param] = value

    return step_parameters

def translate_parameters(ontology:Graph, workflow_graph: Graph, step:URIRef):
    component, implementation = get_step_component_implementation(ontology, workflow_graph, step)
    step_parameters = get_step_parameters_agnostic(ontology, workflow_graph, step)
    print("Implementation: ",implementation)
    print("parameters: ",step_parameters)
    factor_params: List[Tuple[URIRef,Literal]] = translate_factor_params(ontology,workflow_graph, implementation, step_parameters)
    print("Factor params translated:", factor_params)
    numeric_params: List[Tuple[URIRef,Literal]] = translate_numeric_params(ontology,workflow_graph, implementation, step_parameters)
    print("Numeric params translated:", numeric_params)
    return factor_params + numeric_params

def ttl_to_py(ontology: Graph, source_path: str, destination_path: str) -> None:
    tqdm.write('Creating new workflow')

    tqdm.write('\tLoading workflow:', end=' ')
    graph = load_workflow(source_path)
    tqdm.write(next(graph.subjects(RDF.type, tb.Workflow, True)).fragment)

    tqdm.write('\tBuilding steps')
    steps = get_workflow_steps(graph)
    step_paths = []
    for i, step in enumerate(steps):
        python_step_parameters = translate_parameters(ontology, graph, step)
        step_template = environment.get_template("sklearn_step.py.jinja")
        step_file = step_template.render(library = "sklearn",
                                         module = 'svm',
                                         parameters = python_step_parameters,
                                         input_data = ["TrainingDataset"],
                                         function = "SVC",
                                         step_name = "testPhase",
                                         target="survived")
        
        with open(os.path.join(destination_path, 'test.py'), encoding='UTF-8', mode='w') as file:
            file.write(step_file)


    tqdm.write('Done')
    tqdm.write('-' * 50)

def translate_graph(ontology:Graph, source_folder: str, destination_folder: str):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    assert os.path.exists(source_folder)

    workflows = [f for f in os.listdir(source_folder) if f.endswith('.ttl')]
    for workflow in tqdm(workflows):
        source_path = os.path.join(source_folder, workflow)
        destination_path = destination_folder
        ttl_to_py(ontology, source_path, destination_path)



def interactive():
    if easygui is None:
        source_folder = input('Source folder: ')
        destination_folder = input('Destination folder: ')
    else:
        source_folder = easygui.diropenbox('Source folder', 'Source folder', '.')
        print(f'Source folder: {source_folder}')
        destination_folder = easygui.diropenbox('Destination folder', 'Destination folder', '.')
        print(f'Destination folder: {destination_folder}')

    translate_graph(get_ontology(), source_folder, destination_folder)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        translate_graph(get_ontology(), sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        translate_graph(get_ontology(), sys.argv[2], sys.argv[3])
    else:
        print('Interactive usage.')
        print('For non-interactive usage, use:')
        print('\tpython workflow_translator.py <source_folder> <destination_folder>')
        print('\tpython workflow_translator.py --keep <source_folder> <destination_folder>')
        interactive()
