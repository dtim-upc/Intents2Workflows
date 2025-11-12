
import os
import time
from tqdm import tqdm
from datetime import datetime

from graph_queries.intent_queries import get_intent_iri, get_intent_dataset_task
from graph_queries.data_queries import get_dataset_numeric_columns, get_dataset_categorical_columns, get_dataset_columns
from graph_queries.ontology_queries import get_algorithms_from_task
from .abstract_planner import get_algorithms_and_implementations_to_solve_task
from .logical_planner import generate_logical_plans
from .workflow_builder import generate_workflows
from common import *

def add_input_parameters(ontology:Graph, intent_graph:Graph, data_graph:Graph):
    intent_iri = get_intent_iri(intent_graph)
    dataset, task, algorithm = get_intent_dataset_task(intent_graph, intent_iri)

    all_cols = get_dataset_columns(data_graph, dataset)
    cat_cols = get_dataset_categorical_columns(data_graph, dataset)
    num_cols = get_dataset_numeric_columns(data_graph, dataset)
    exp_params = []#graph_queries.get_exposed_parameters(ontology, task, algorithm)

    for exp_param in exp_params:
        option_columns = []
        if 'CATEGORICAL' in exp_param['value']:
            option_columns = cat_cols
        elif 'NUMERICAL' in exp_param['value']:
            option_columns = num_cols
        else:
            option_columns = all_cols

        if 'COMPLETE' in exp_param['value']:
            option_columns.append('<RowID>')

        if 'INCLUDED' in exp_param['condition']:
            param_val = []
            col_num = int(input(f"How many columns do you want to enter for {exp_param['label']} parameter?"))
            for i in range(col_num):
                param_val.append(input(f"Enter a value for {exp_param['label']} from the following: {option_columns}"))
        else:
            param_val = input(f"Enter a value for {exp_param['label']} from the following: {option_columns}")

        intent_graph.add((intent_iri, tb.specifiesValue, Literal(param_val)))
        intent_graph.add((Literal(param_val), tb.forParameter, exp_param['exp_param']))

def interactive():
    intent_graph = get_graph_xp()
    intent = input('Introduce the intent name [ClassificationIntent]: ') or 'VisualizationIntent' #or 'ClassificationIntent'
    data = input('Introduce the annotated dataset path [./titanic.ttl]: ') or './titanic.ttl'
    task = input('Introduce the task name [Classification]: ') or 'Classification'


    intent_graph.add((ab.term(intent), RDF.type, tb.Intent))
    intent_graph.add((ab.term(intent), tb.overData, ab.term(data)))
    intent_graph.add((cb.term(task), tb.tackles, ab.term(intent)))

    data_graph = Graph().parse(f'{data}',format="turtle")


    ontology = get_ontology_graph()

    if task == 'DataVisualization':
        algos = [alg.fragment for alg in get_algorithms_from_task(ontology, cb.term(task))]
        vis_algorithm = str(input(f'Choose a visualization algorithm from the following (case-sensitive):{algos}'))
        if vis_algorithm is not None:
            intent_graph.add((ab.term(intent), tb.specifies, cb.term(vis_algorithm)))

    component_percentage = float(input('Choose a threshold component percentage (for the preprocessing components) [100, 75, 50, 25] (%): ') or 100)/100.0
    complexity = int(input("Choose the complexity of the generated workflows [0,1,2]: ") or 2)

    intent_graph.add((ab.term(intent), tb.has_component_threshold, Literal(component_percentage)))
    intent_graph.add((ab.term(intent), tb.has_complexity, Literal(complexity)))

    folder = input('Introduce the folder to save the workflows: ')
    if folder == '':
        folder = f'./workflows/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}/'
        tqdm.write(f'No folder introduced, using default ({folder})')
    if not os.path.exists(folder):
        tqdm.write('Directory does not exist, creating it')
        os.makedirs(folder)

    shape_graph = Graph()
    shape_graph.parse('./shapeGraph.ttl')

    #add_input_parameters(ontology,intent_graph,data_graph)

    t = time.time()
    solving_algs, solving_impls = get_algorithms_and_implementations_to_solve_task(ontology, shape_graph, intent_graph, log=True)
    logical_plans = generate_logical_plans(ontology, shape_graph, intent_graph, data_graph, solving_impls, log=True)
    workflows = generate_workflows(ontology, intent_graph, data_graph, logical_plans, run_transformations=False)
    t = time.time() - t

    print(f'Workflows built in {t} seconds')

    for wg in workflows:
        workflow_name = next(wg.subjects(RDF.type, tb.Workflow, unique=True)).fragment
        print(workflow_name)
        wg.serialize(os.path.join(folder, f'{workflow_name}.ttl'), format='turtle')
    print(f'Workflows saved in {folder}')

interactive()