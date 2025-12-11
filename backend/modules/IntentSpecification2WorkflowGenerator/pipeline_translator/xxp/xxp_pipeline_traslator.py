import shutil
import sys
import os
import jinja2
from typing import Dict, Tuple, List
from tqdm import tqdm
import tempfile
import zipfile

from common import *
from graph_queries.workflow_queries import get_workflow_steps, get_step_component, get_step_input_data, get_step_output_data, \
    get_workflow_intent_number, get_workflow_connections
from graph_queries.ontology_queries import get_component_implementation, get_implementation_task, get_implementation_input_specs
from graph_queries.intent_queries import get_intent_iri, get_intent_dataset
from graph_queries.data_queries import get_dataset_path, get_dataset_uri
from pipeline_translator.python import python_pipeline_translator
from pipeline_translator.core.translator_common_functions import load_workflow

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

template_base = os.path.dirname(os.path.abspath(__file__))
template_paths = [
    os.path.join(template_base, "pipeline_translator", "xxp", "templates"),
    os.path.join(template_base, "templates")
]
environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_paths))

class WorkflowXXP:
    def __init__(self,name:str, graph:Graph):
        self.name = name
        self.steps_task = {}
        self.tasks_component = {}
        self.graph = graph
    
    def add_step(self,name:str, task:str, component:str):
        self.steps_task[name] = task
        self.tasks_component[task] = component

    @property
    def abstract_workflow_id(self):
        return hash(tuple(self.tasks_component.keys()))
    
    @property
    def tasks(self):
        return self.tasks_component.keys()
    
    
    def get_external_input(self):
        dataset = get_dataset_uri(self.graph)
        return {
                "name":dataset.fragment,
                "path": get_dataset_path(self.graph, dataset)
                }
    
    def get_external_output(self):
        return {
            "name":"workflowOutput",
            "path": "/outputs/output.csv"
        }
    
    def get_connection_mappings(self, external_input, external_output):
        connections = get_workflow_connections(self.graph)

        mappings=[]
        for sourceStep, destinationStep, sourcePort, destinationPort in connections:
            if sourceStep.fragment in self.steps_task and destinationStep.fragment in self.steps_task:
                mappings.append((self.steps_task[sourceStep.fragment], 
                                self.steps_task[destinationStep.fragment], 
                                sourcePort, destinationPort))
            elif sourceStep.fragment not in self.steps_task:
                mappings.append((external_input, 
                                 self.steps_task[destinationStep.fragment], 
                                 None, destinationPort))
            else:
                mappings.append((self.steps_task[sourceStep.fragment], 
                external_output, 
                sourcePort, None))
        return mappings
        



def generate_task_python(python_step:str, task:str, inputs:List[URIRef], outputs:List[URIRef]):
    task_python_template = environment.get_template('task.py.jinja')
    task_python = task_python_template.render(python_function = python_step,
                                    python_function_name = task,
                                    inputs=inputs,
                                    outputs=outputs)
    return task_python

def generate_task_xxp(task:str, inputs:List[URIRef], outputs:List[URIRef]):
    task_xxp_template = environment.get_template("task.xxp.jinja")
    task_xxp = task_xxp_template.render(task = task,
                                        inputs = inputs,
                                        outputs = outputs)
    return task_xxp

        
def adapt_io(ios:list[URIRef]) -> List[str]:
    adapted_io = []
    for io in ios:
        start = io.fragment.find('step')
        adapted_io.append(io.fragment[start:].replace('-','_') if start != -1 else io.fragment)
    return adapted_io

def get_xxp_workflow(ontology: Graph, workflow_graph:Graph) -> WorkflowXXP:
    workflow_steps = get_workflow_steps(workflow_graph)

    intent_iri = get_intent_iri(workflow_graph)
    dataset_uri = get_intent_dataset(workflow_graph, intent_iri)
    or_dataset_path = get_dataset_path(workflow_graph, dataset_uri)

    workflow_name = f"{intent_iri.fragment}"

    workflow = WorkflowXXP(workflow_name,workflow_graph)

    for step in workflow_steps[1:-1]: #ignore reader and writer
        component = get_step_component(workflow_graph,step)
        implementation = get_component_implementation(ontology, component)
        task = get_implementation_task(ontology, implementation).fragment
        if (implementation, RDF.type, tb.ApplierImplementation) in ontology:
            task += '_test'


        component_name = component.fragment.replace('component','').replace('-','')

        #subfolder_name = f'{component_name}'
        #subfolder = os.path.join(folder, subfolder_name)

        workflow.add_step(step.fragment, task, component_name)

    return workflow


        # if not os.path.exists(subfolder): #if subfolder exists, task already present. We avoid repetitions when translating multiple workflows
        #     os.mkdir(subfolder)
        #     python_step, step_name, inputs, outputs = python_pipeline_translator.translate_step(ontology, workflow_graph, step, 
        #                                                                                         function_name=component_name)
        #     inputs_adapted = adapt_io(inputs)
        #     outputs_adapted = adapt_io(outputs)

        #     task_python = generate_task_python(python_step,component_name, inputs_adapted, outputs_adapted)
        #     task_xxp = generate_task_xxp(component_name, inputs_adapted, outputs_adapted)

        #     with open(os.path.join(subfolder, 'task.py'), encoding='UTF-8', mode='w') as file:
        #         file.write(task_python)
        #     with open(os.path.join(subfolder, 'task.xxp'), encoding='UTF-8', mode='w') as file:
        #         file.write(task_xxp)


    #connections = get_workflow_connections(workflow_graph)
    #connection_mappings = create_connection_mappings(connections, steps_task)

    # workflow_template = environment.get_template("workflow.xxp.jinja")
    # translation = workflow_template.render(workflow_name = workflow_name,
    #                                        steps = steps_struct,
    #                                        data_flow = connection_mappings
    #                                        )
    # with open(os.path.join(folder, f'{workflow_name}.xxp'), encoding='UTF-8', mode='w') as file:
    #         file.write(translation)

def package_workflow(folder: str, destination: str) -> None:
    print("Destination", destination)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
        print("Folder", folder)
        for root, _, files in os.walk(folder):
            for file in files:
                print("FILE", file)
                file_path = os.path.join(root, file)
                archive_path = os.path.relpath(file_path, folder)
                #workflow_name = os.path.splitext(os.path.basename(destination))[0]
                zipf.write(file_path, arcname=os.path.join(archive_path))

    


def translate_graph_folder(ontology:Graph, source_folder: str, destination_folder: str):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    assert os.path.exists(source_folder)

    tqdm.write('\tCreating temp folder: ', end='')
    temp_folder = tempfile.mkdtemp()
    tqdm.write(temp_folder)

    workflows = [f for f in os.listdir(source_folder) if f.endswith('.ttl')]
    xxp_workflows:Dict[int,List[WorkflowXXP]] = {}

    for workflow in tqdm(workflows):

        tqdm.write('\tLoading workflow:', end=' ')
        source_path = os.path.join(source_folder, workflow)
        graph = load_workflow(source_path)
        tqdm.write(next(graph.subjects(RDF.type, tb.Workflow, True)).fragment)

        tqdm.write('\tCreating files')
        workflow = get_xxp_workflow(ontology, graph)
        id = workflow.abstract_workflow_id

        if id not in xxp_workflows:
            xxp_workflows[id] = []

        xxp_workflows[id].append(workflow)

    assembled_names = []
    abstract_workflows = []
    for i,assemblies in enumerate(xxp_workflows.values()):
        assert len(assemblies) > 0
        base_workflow = assemblies[0]
        base_name = f"{base_workflow.name}Workflow{i}"
        external_input = base_workflow.get_external_input()
        external_output = base_workflow.get_external_output()

        data_flow = base_workflow.get_connection_mappings(external_input["name"], external_output["name"])
        tasks = base_workflow.tasks
        assembly_workflows = []
        abstract_workflows.append(f'/test/{base_workflow.name}.xxp')

        for a in assemblies:
            name = f"{a.name}AssembledWorkflow{get_workflow_intent_number(a.graph)}"
            assembly_workflows.append({
                "name":name,
                "tasks_implementation":a.tasks_component.items()
            })

            assembled_names.append(name)

        workflow_template = environment.get_template("workflow.xxp.jinja")
        translation = workflow_template.render(workflow_name = base_name,
                                               tasks = tasks,
                                               data_flow = data_flow,
                                               inputs = [external_input],
                                               outputs = [external_output],
                                               workflows = assembly_workflows
                                            )
        
        with open(os.path.join(temp_folder, f'{base_name}.xxp'), encoding='UTF-8', mode='w') as file:
            file.write(translation)
        

    experiment_template = environment.get_template("experiment.xxp.jinja")
    experiment_translation = experiment_template.render(experiment_name = "DemoExperiment",
                                            workflows=assembled_names,
                                            imports = abstract_workflows
                                        )
    with open(os.path.join(temp_folder, f'experiments.xxp'), encoding='UTF-8', mode='w') as file:
            file.write(experiment_translation)
    
    
    destination_path = os.path.join(destination_folder,'xxp_translation.zip')
    package_workflow(temp_folder, destination_path)

    tqdm.write('\tRemoving temp folder')
    shutil.rmtree(temp_folder)
    tqdm.write('Done')
    tqdm.write('-' * 50)

    return destination_path
