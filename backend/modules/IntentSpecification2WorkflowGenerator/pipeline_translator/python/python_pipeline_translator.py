import os
import sys
from typing import Dict
import jinja2
from rdflib import Graph, URIRef, RDF


from tqdm import tqdm

translator_dir = os.path.join(os.path.abspath(os.path.join('..')))
sys.path.append(translator_dir)

root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

environment = jinja2.Environment(loader=jinja2.FileSystemLoader(["pipeline_translator/python/templates", "templates"])) #the double path ensures expected performance on terminal and api execution
from ..core.translator_common_functions import *
from ..core.parameter_translator import translate_parameters
from graph_queries.workflow_queries import get_step_component, get_workflow_steps, get_step_parameters_agnostic, get_step_input_data, get_step_output_data, get_workflow_connections
from graph_queries.ontology_queries import get_component_implementation, get_implementation_task, is_predictor
from ..core.translator_common_functions import get_implementation_engine_conditional


try:
    import easygui # type: ignore
except ImportError:
    easygui = None


def get_python_module(ontology: Graph, implementation: URIRef):
    return next(ontology.objects(implementation, tb.python_module, unique=True),None)

def get_python_function(ontology: Graph, implementation: URIRef):
    return next(ontology.objects(implementation, tb.python_function, unique=True),None)

def get_template(ontology: Graph, implementation: URIRef):
    return next(ontology.objects(implementation, tb.template, unique=True),None)

def split_parameters(ontology: Graph, params: Dict[str,str]):
    control_params = {}
    function_params = {}
    for param_uri, param_data in params.items():
        key, value = param_data
        if next(ontology.objects(param_uri, tb.isControlParameter,unique=True),False):
            control_params[key] = value
        else:
            function_params[key] = value
    return control_params, function_params

def translate_step(ontology: Graph, workflow_graph:Graph, step:URIRef, inherited_params:dict = {}, function_name = None):
    component = get_step_component(workflow_graph, step)
    implementation = get_component_implementation(ontology, component)
    task = get_implementation_task(ontology, implementation).fragment
    if is_predictor(ontology, implementation):
        task += '_predictor'

    step_parameters = get_step_parameters_agnostic(workflow_graph, step)
    engine_implementation = get_implementation_engine_conditional(ontology, implementation, cb.Python, step_parameters)
    python_step_parameters = translate_parameters(ontology, step_parameters, engine_implementation)
    cp, function_params = split_parameters(ontology, python_step_parameters)
    inherited_params.update(cp)
    #print("Control:",control_params) 
    #print("Function:",function_params)

    python_module = get_python_module(ontology, engine_implementation)
    python_function = get_python_function(ontology, engine_implementation)
    template = get_template(ontology, engine_implementation)

    inputs = get_step_input_data(workflow_graph, step)
    outputs = get_step_output_data(workflow_graph, step)

    step_name = function_name if not function_name is None else task

    step_template = environment.get_template(f"{template}.py.jinja")

    #tqdm.write("RENDER parameters:", python_step_parameters)
    
    step_file = step_template.render(module = python_module,
                                        parameters = function_params.items(),
                                        control = inherited_params,
                                        function = python_function,
                                        step_name = step_name,
                                        inputs = [i for i in range(len(inputs))],
                                        outputs = [i for i in range(len(outputs))])
    return step_file, task, inputs, outputs, python_module


def translate_graph(ontology: Graph, source_path: str, destination_path: str) -> None:
    tqdm.write('Creating new workflow')

    tqdm.write('\tLoading workflow:', end=' ')
    graph = load_workflow(source_path)
    tqdm.write(next(graph.subjects(RDF.type, tb.Workflow, True)).fragment)


    tqdm.write('\tBuilding steps')
    steps = get_workflow_steps(graph)
    steps_struct = {}
    control_params = {}
    for step in tqdm(steps):
        #TODO custom step class to solve this output
        step_file, task, inputs, outputs, dependences = translate_step(ontology, graph, step, inherited_params=control_params)
        
        steps_struct[step] = {'task':task, 'inputs': [None]*len(inputs), 'outputs':[task+str(i) for i in range(len(outputs))], 'file': step_file}
    
    connections = get_workflow_connections(graph)
 
    for source_step, destination_step, source_port, destination_port in connections:
        steps_struct[destination_step]['inputs'][int(destination_port)] = steps_struct[source_step]['outputs'][int(source_port)]

    main_template = environment.get_template('main.py.jinja')
    main_file = main_template.render(steps = steps,
                                     step_files = steps_struct)


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
