
import os
import time
from tqdm import tqdm
from datetime import datetime

from optimized_pipeline_generator import build_workflows
from common import *
import graph_queries

def interactive():
    intent_graph = get_graph_xp()
    intent = input('Introduce the intent name [ClassificationIntent]: ') or 'VisualizationIntent' #or 'ClassificationIntent'
    data = input('Introduce the dataset name [titanic.csv]: ') or 'titanic.csv'
    task = input('Introduce the task name [Classification]: ') or 'Classification'


    intent_graph.add((ab.term(intent), RDF.type, tb.Intent))
    intent_graph.add((ab.term(intent), tb.overData, ab.term(data)))
    intent_graph.add((cb.term(task), tb.tackles, ab.term(intent)))


    ontology = get_ontology_graph()

    if task == 'DataVisualization':
        algos = [alg.fragment for alg in graph_queries.get_algorithms_from_task(ontology, cb.term(task))]
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
    t = time.time()
    build_workflows(ontology, shape_graph, intent_graph, folder, log=True)
    t = time.time() - t

    print(f'Workflows built in {t} seconds')
    print(f'Workflows saved in {folder}')

interactive()