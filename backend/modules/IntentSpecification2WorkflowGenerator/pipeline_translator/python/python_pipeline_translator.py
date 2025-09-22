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
import rdflib

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


def translate_text_params(ontology:URIRef, workflow_graph: Graph, implementation:URIRef, step_parameters: Dict[URIRef,Literal]):
    python_params = []
    text_params = get_engine_text_params(ontology,implementation,engine='Python')
    target = None

    print("Text params:", text_params)

    for param in text_params:
        base_param = get_base_param(ontology, param)
        if base_param in step_parameters.keys():
            value = step_parameters[base_param]
        else:
            value = get_default_value(ontology, param)

        if isinstance(value, rdflib.Literal):
            print("Transformant text literal...", value)
            value = value.toPython()
        else:
            print("No necessita transformació:",value)

        key = next(ontology.objects(param, tb.python_key, unique=True))
        if key == Literal('Target'):# Extract target from the parameters. Key Target specified as python_key in the ontology
            target = value
        else:
            python_params.append((key, value))
    return python_params, target


def translate_factor_params(ontology:URIRef, workflow_graph: Graph, implementation:URIRef, step_parameters: Dict[URIRef,Literal]):
    python_params = []
    factor_params = get_engine_factor_params(ontology,implementation,engine='Python')

    print("Factor params:", factor_params)

    for param in factor_params:
        base_param = get_base_param(ontology, param)
        if base_param in step_parameters.keys():
            value = translate_factor_level(ontology, base_param, step_parameters[base_param], param)
        else:
            value = get_default_value(ontology, param)
        
        if isinstance(value, rdflib.Literal):
            print("Transformant factor literal...", value)
            value = value.toPython()
        else:
            print("No necessita transformació:",value)

        key = next(ontology.objects(param, tb.python_key, unique=True))
        python_params.append((key, value))
    return python_params


def calculate(term1, term2, operation):
    print("Calculant", term1, operation, term2)
    if term1 is None or (term2 is None and operation not in ['COPY', "SQRT"]):
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
    elif operation == "EQ":
        return term1 == term2
    elif operation == 'COPY':
        return term1
    else:
        raise Exception("Invalid operation: "+operation)


def compute_algebraic_expression(ontology: Graph, expression: URIRef, step_parameters:URIRef):
    term1, term2, operation = unpack_expression(ontology,expression)

    print("Algebraic expression", term1, operation, term2)

    assert not term1 is None and not operation is None

    operation = URIRef(operation).fragment
    assert (term2 is None and operation in ['COPY', 'SQRT']) or not term2 is None


    def compute_term_value(term):
        type = get_term_type(ontology, term)
        
        if type == "Parameter":
            if term in step_parameters.keys():
                value = step_parameters[term].toPython()
            else:
                print("Term",term,"not present in step parameters. Using default value")
                value= None
        elif type =="Literal":
                value = term.toPython()
        elif type == "NONE":
                value = None
        elif type == "AlgebraicExpression":
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
        print("PARÀMETRE:",param)
        alg_expression = get_algebraic_expression(ontology, param)
        value = compute_algebraic_expression(ontology, alg_expression, step_parameters)
        if value is None:
            value = get_default_value(ontology, param)
            print("El default value és:",value, type(value))
        if value == cb.NONE:
            print(value, "És NULL")
            value = None
        elif isinstance(value, rdflib.Literal):
            print("Transformant literal...", value)
            value = value.toPython()
        else:
            print("No necessita transformació:",value, type(value))
        
        key = next(ontology.objects(param, tb.python_key, unique=True))
        python_params.append((key, value))
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

def translate_parameters(ontology:Graph, workflow_graph: Graph, step:URIRef, implementation:URIRef):
    step_parameters = get_step_parameters_agnostic(ontology, workflow_graph, step)
    print("Implementation: ",implementation)
    print("parameters: ",step_parameters)

    text_params, target = translate_text_params(ontology,workflow_graph, implementation, step_parameters)
    print("Target:",target)
    print("Text params translated:", text_params)
    factor_params: List[Tuple[URIRef,Literal]] = translate_factor_params(ontology,workflow_graph, implementation, step_parameters)
    print("Factor params translated:", factor_params)
    numeric_params: List[Tuple[URIRef,Literal]] = translate_numeric_params(ontology,workflow_graph, implementation, step_parameters)
    print("Numeric params translated:", numeric_params)
    return text_params + factor_params + numeric_params, target

def get_python_module(ontology: Graph, implementation: URIRef):
    return next(ontology.objects(implementation, tb.python_module, unique=True),None)

def get_python_function(ontology: Graph, implementation: URIRef):
    return next(ontology.objects(implementation, tb.python_function, unique=True),None)

def get_template(ontology: Graph, implementation: URIRef):
    return next(ontology.objects(implementation, tb.template, unique=True),None)

def translate_graph(ontology: Graph, source_path: str, destination_path: str) -> None:
    tqdm.write('Creating new workflow')

    tqdm.write('\tLoading workflow:', end=' ')
    graph = load_workflow(source_path)
    tqdm.write(next(graph.subjects(RDF.type, tb.Workflow, True)).fragment)

    tqdm.write('\tBuilding steps')
    steps = get_workflow_steps(graph)
    steps_struct = {}
    target = None
    for i, step in enumerate(steps):
        component, implementation = get_step_component_implementation(ontology, graph, step)
        task = get_implementation_task(ontology, implementation).fragment
        if is_predictior(ontology, implementation):
            task += '_predictor'
        python_step_parameters, new_target = translate_parameters(ontology, graph, step, implementation)
        target = new_target if not new_target is None else target #Applier does not have information about the target, so it should be given by the learner

        engine_implementation = get_engine_implementation(ontology, implementation, 'Python')
        python_module = get_python_module(ontology, engine_implementation)
        python_function = get_python_function(ontology, engine_implementation)
        template = get_template(ontology, engine_implementation)

        inputs = get_step_inputs(graph, step)
        outputs = get_step_outputs(graph, step)

        step_template = environment.get_template(f"{template}.py.jinja")

        print("RENDER parameters:", python_step_parameters)
        
        step_file = step_template.render(module = python_module,
                                         parameters = python_step_parameters,
                                         function = python_function,
                                         step_name = task,
                                         target=target,
                                         inputs = [i for i in range(len(inputs))],
                                         outputs = [i for i in range(len(outputs))])
        steps_struct[step] = {'task':task, 'inputs': [None]*len(inputs), 'outputs':[task+str(i) for i in range(len(outputs))], 'file': step_file}
    
    connections = get_workflow_connections(graph)

    for source_step, destination_step, source_port, destination_port in connections:
        steps_struct[destination_step]['inputs'][int(destination_port)] = steps_struct[source_step]['outputs'][int(source_port)]

    main_template = environment.get_template('main.py.jinja')

    main_file = main_template.render(steps = steps,
                                     step_files = steps_struct)
    

    workflow_name = os.path.splitext(os.path.basename(source_path))[0] #TODO chane to pathlib
    print('Wname:',workflow_name)
    with open(os.path.join(destination_path), encoding='UTF-8', mode='w') as file:
            file.write("#This script has been automatically generated by I2WG")
    
    with open(os.path.join(destination_path), encoding='UTF-8', mode='a') as file:
        for step in steps:
            file.write(steps_struct[step]['file'])
        file.write(main_file)


    tqdm.write('Done')
    tqdm.write('-' * 50)

def translate_graph_folder(ontology:Graph, source_folder: str, destination_folder: str):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    assert os.path.exists(source_folder)

    workflows = [f for f in os.listdir(source_folder) if f.endswith('.ttl')]
    for workflow in tqdm(workflows):
        source_path = os.path.join(source_folder, workflow)
        destination_path = destination_folder
        translate_graph(ontology, source_path, destination_path)



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
        translate_graph_folder(get_ontology(), sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        translate_graph_folder(get_ontology(), sys.argv[2], sys.argv[3])
    else:
        print('Interactive usage.')
        print('For non-interactive usage, use:')
        print('\tpython workflow_translator.py <source_folder> <destination_folder>')
        print('\tpython workflow_translator.py --keep <source_folder> <destination_folder>')
        interactive()
