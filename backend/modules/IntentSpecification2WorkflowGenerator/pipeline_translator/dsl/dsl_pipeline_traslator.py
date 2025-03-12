import sys
import os
import jinja2

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from translator_common_functions import *

environment = jinja2.Environment(loader=jinja2.FileSystemLoader(["pipeline_translator/dsl/templates", "templates"])) #the double path ensures expected performance on terminal and api execution

def get_task_implementations(ontology: Graph, workflow_graph:Graph) -> Tuple[List[URIRef],List[str]]:
    tasks = []
    task_implementations = {}

    steps = get_workflow_steps(workflow_graph)
    for step in steps:
        component, implementation = get_step_component_implementation(ontology,workflow_graph,step)
        task = get_implementation_task(ontology, implementation).fragment
        in_specs = get_implementation_input_specs(ontology, implementation)
        print(in_specs)
        if any(cb.TrainTabularDatasetShape in spec for spec in in_specs):
            tasks.append("ModelTrain")
            task_implementations["ModelTrain"] = component.fragment
            tasks.append("ModelPredict")
            task_implementations["ModelPredict"] = component.fragment + "_predictor"
        elif tb.ApplierImplementation not in ontology.objects(implementation, RDF.type):
            tasks.append(task)
            task_implementations[task] = component.fragment
    
    return tasks, task_implementations

def tranlate_graph_to_dsl(ontology: Graph, workflow_graph:Graph) -> str:
    tasks, task_implementations = get_task_implementations(ontology, workflow_graph)
    intent_name = get_workflow_intent_name(workflow_graph)
    workflow_name = 'Workflow_' + str(get_workflow_intent_number(workflow_graph))


    workflow_template = environment.get_template("workflow.py.jinja")
    translation = workflow_template.render(intent_name = intent_name, 
                                           workflow_name = workflow_name,
                                           tasks = tasks,
                                           task_implementations = task_implementations)

    with open('test.txt', mode='w') as f:
        f.write(translation)

    return translation

