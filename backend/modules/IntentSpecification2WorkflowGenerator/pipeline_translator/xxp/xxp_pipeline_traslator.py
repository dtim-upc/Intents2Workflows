import sys
import os
import jinja2
from typing import Tuple, List

from common import *
from graph_queries.workflow_queries import get_workflow_steps, get_step_component, get_step_input_data, get_step_output_data, get_workflow_intent_number
from graph_queries.ontology_queries import get_component_implementation, get_implementation_task, get_implementation_input_specs
from graph_queries.intent_queries import get_intent_iri, get_intent_dataset
from graph_queries.data_queries import get_dataset_path
from pipeline_translator.python import python_pipeline_translator

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

template_base = os.path.dirname(os.path.abspath(__file__))
template_paths = [
    os.path.join(template_base, "pipeline_translator", "xxp", "templates"),
    os.path.join(template_base, "templates")
]
environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_paths))

def get_task_implementations(ontology: Graph, workflow_graph:Graph) -> Tuple[List[URIRef],List[str]]:
    tasks = []
    task_implementations = {}

    steps = get_workflow_steps(workflow_graph)

    for step in steps:
        component = get_step_component(workflow_graph,step)
        implementation = get_component_implementation(ontology, component)
        task = get_implementation_task(ontology, implementation).fragment
        in_specs = get_implementation_input_specs(ontology, implementation)
    
        python_step, step_name, inputs, outputs = python_pipeline_translator.translate_step(ontology, workflow_graph, step)
        task_python_template = environment.get_template('task.py.jinja')
        task_python = task_python_template.render(python_function = python_step,
                                    python_function_name = task,
                                    inputs=inputs,
                                    outputs=outputs)
        with open(f'./{task}.py', mode='w') as f:
            f.write(task_python)

        task_xxp_template = environment.get_template("task.xxp.jinja")
        task_xxp = task_xxp_template.render(task = task,
                                            inputs = inputs,
                                            outputs = outputs)
        with open(f'./{task}.xxp', mode='w') as f:
            f.write(task_xxp)

        if any(cb.TrainTabularDatasetShape in spec for spec in in_specs):
            tasks.append("ModelTrain")
            task_implementations["ModelTrain"] = component.fragment
            tasks.append("ModelPredict")
            task_implementations["ModelPredict"] = component.fragment + "_predictor"
        elif tb.ApplierImplementation not in ontology.objects(implementation, RDF.type):
            tasks.append(task)
            task_implementations[task] = component.fragment
    assert 3 == 2
    
    return tasks, task_implementations

def get_steps_io(ontology:Graph, workflow_graph:Graph)->Tuple[List[List[URIRef]], List[List[URIRef]]]:
    steps = get_workflow_steps(workflow_graph)
    inputs = {}
    outputs = {}

    for step in steps:
        component = get_step_component(workflow_graph,step)
        implementation = get_component_implementation(ontology, component)
        task = get_implementation_task(ontology, implementation).fragment
        step_inputs = get_step_input_data(workflow_graph, step)
        step_outputs = get_step_output_data(workflow_graph, step)
        inputs[task] = step_inputs
        outputs[task] = step_outputs
    
    return inputs,outputs

def tranlate_graph_to_dsl(ontology: Graph, workflow_graph:Graph, header=True) -> str:
    tasks, task_implementations = get_task_implementations(ontology, workflow_graph)
    intent_iri = get_intent_iri(workflow_graph)
    workflow_name = 'Workflow_' + str(get_workflow_intent_number(workflow_graph))
    inputs, outputs = get_steps_io(ontology, workflow_graph)
    dataset_uri = get_intent_dataset(workflow_graph, intent_iri)
    or_dataset_path = get_dataset_path(workflow_graph, dataset_uri)

    workflow_template = environment.get_template("workflow.py.jinja")
    translation = workflow_template.render(intent_name = intent_iri.fragment, 
                                           workflow_name = workflow_name,
                                           tasks = tasks,
                                           task_implementations = task_implementations,
                                           header = header,
                                           inputs = inputs,
                                           outputs = outputs,
                                           path = or_dataset_path)

    with open('test.txt', mode='w') as f:
        f.write(translation)

    return translation

def translate_graphs_to_dsl(ontology:Graph, workflow_graphs:List[Graph]) -> str:
    trans = []
    header = True
    for w in workflow_graphs:
        trans.append(tranlate_graph_to_dsl(ontology, w, header))
        header = False
    
    return "\n".join(trans)

