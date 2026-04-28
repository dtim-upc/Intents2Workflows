from openml import tasks, OpenMLDataset, study, OpenMLClassificationTask, evaluations, runs
import pandas as pd
import os, sys

from rdflib import Graph, URIRef, Literal
from owlrl import DeductiveClosure, OWLRL_Semantics

root_dir = os.path.join(os.path.abspath(os.path.join('..')))
sys.path.append(root_dir)

root_dir2 = os.path.join(os.path.abspath(os.path.join('../../../api')))
sys.path.append(root_dir2)


from pipeline_generator import abstract_planner, logical_planner, workflow_builder
from pipeline_translator.python import python_pipeline_translator
from dataset_annotator import annotator
from common import get_ontology_graph, get_graph_xp, ab, tb, cb, RDF, get_tbox

print("Loading ontology...")
ontology = get_ontology_graph()
tbox_graph = get_tbox()
print("Ontology loaded!")
    


s = study.get_suite(271)
for task_id in s.tasks:
    task:OpenMLClassificationTask = tasks.get_task(task_id)
    data: OpenMLDataset = task.get_dataset()
    target = task.target_name
    X, y, categorical_indicator, attribute_names= data.get_data()
    df = pd.DataFrame(X, columns=attribute_names)

    df.to_csv(f"./autoOntology/data/{data.name}.csv")

    dl = annotator.load_dataset(df,name=f"{data.name}")

    node, annotations = annotator.annotate_dataset(dl, label=target)

    data_graph = tbox_graph+annotations
    DeductiveClosure(OWLRL_Semantics).expand(data_graph)

    intent_graph = get_graph_xp()

    problem_to_solve = cb.SupervisedLearning
    intent_name = f"{task.task_id}Intent"
    dataset_name = dl.getFileMetadata().get("name")

    intent_graph.add((ab.term(intent_name), RDF.type, tb.Intent))
    intent_graph.add((ab.term(intent_name), tb.overData, ab.term(dataset_name)))
    intent_graph.add((problem_to_solve, tb.tackles, ab.term(intent_name)))

    intent_graph.add((ab.term(intent_name), tb.has_component_threshold, Literal(1.0)))
    intent_graph.add((ab.term(intent_name), tb.has_complexity, Literal(1)))
    
    scores, algorithms = abstract_planner.get_algorithms_and_implementations_to_solve_task(ontology=ontology, shape_graph=None, intent_graph=intent_graph, data_graph=data_graph)
    print("abstract plans",algorithms)
    
    logical_plans = logical_planner.generate_logical_plans(ontology=ontology, shape_graph=None, intent_graph = intent_graph, data_graph=data_graph, pot_impls=[
        cb["implementation-svc"],
        cb["implementation-randomforestclassifier"],])
    
    print("logical plans", logical_plans)

    plan = logical_plans['logical_plans'][0]
    lastplan = logical_plans['logical_plans'][-1]

    first_logical_plan = {
        plan['name']: (plan['plan'], plan['cols']),
        lastplan['name']: (lastplan['plan'], lastplan['cols'])
    }

    print("first_logical_plan", first_logical_plan)

    workflows = workflow_builder.generate_workflows(ontology=ontology, intent_graph=intent_graph, data_graph=data_graph, logical_plans=(first_logical_plan))

    print("workflows", workflows)

    for name,graph in workflows.items():
        graph.serialize(destination=f'./autoOntology/workflows/{name}.ttl', format='ttl')



    python_pipeline_translator.translate_graph_folder(ontology=ontology, source_folder='./autoOntology/workflows', destination_folder='./autoOntology/scripts/')

    input("Execute next task?")


    continue

    #print(X, y, categorical_indicator, attribute_names)
    evals = evaluations.list_evaluations(
    function="area_under_roc_curve",
    tasks=[task_id])

    result = pd.DataFrame([
    {"run_id": v.run_id, "value": v.value}
    for v in evals.values()
    ])
    print("RUNS",len(evals))

    if len(evals) > 0:
        print(result.sort_values("value", ascending=False).head())

