import subprocess

from openml import tasks, OpenMLDataset, study, OpenMLClassificationTask, evaluations, runs
import pandas as pd
import os, sys
from pathlib import Path
import json
import csv
import time

from rdflib import Graph, URIRef, Literal
from owlrl import DeductiveClosure, OWLRL_Semantics

root_dir = os.path.join(os.path.abspath(os.path.join('..')))
sys.path.append(root_dir)

root_dir2 = os.path.join(os.path.abspath(os.path.join('../../../api')))
sys.path.append(root_dir2)


from pipeline_generator import abstract_planner, logical_planner, workflow_builder
from pipeline_translator.python import python_pipeline_translator
from dataset_annotator import annotator
from graph_queries.workflow_queries import get_workflow_steps, get_step_component
from common import get_ontology_graph, get_graph_xp, ab, tb, cb, RDF, get_tbox


def get_component_plan(workflow:Graph):
    steps = get_workflow_steps(workflow)

    components = []
    for s in steps:
        c = get_step_component(workflow, s)
        components.append(c.fragment)
    return components

print("Loading ontology...")
ontology = get_ontology_graph()
tbox_graph = get_tbox()
print("Ontology loaded!")
    


s = study.get_suite(271)
for i, task_id in enumerate(s.tasks):

    if i == 1:
        continue

    task:OpenMLClassificationTask = tasks.get_task(task_id)
    data: OpenMLDataset = task.get_dataset()
    target = task.target_name
    X, y, categorical_indicator, attribute_names= data.get_data()
    df = pd.DataFrame(X, columns=attribute_names)

    df.to_csv(f"./autoOntology/data/{data.name}.csv", index=False)

    print("Executing annotator")
    start = time.perf_counter()
    dl = annotator.load_dataset(df,name=f"{data.name}")
    node, annotations = annotator.annotate_dataset(dl, label=target)
    end = time.perf_counter()
    an_time = end - start
    print(f"Execution of annotator finished in {an_time}s")

    data_graph = tbox_graph+annotations
    DeductiveClosure(OWLRL_Semantics).expand(data_graph)

    intent_graph = get_graph_xp()

    problem_to_solve = cb.Classification#cb.SupervisedLearning
    intent_name = f"{task.task_id}Intent"
    dataset_name = dl.getFileMetadata().get("name")

    intent_graph.add((ab.term(intent_name), RDF.type, tb.Intent))
    intent_graph.add((ab.term(intent_name), tb.overData, ab.term(dataset_name)))
    intent_graph.add((problem_to_solve, tb.tackles, ab.term(intent_name)))

    intent_graph.add((ab.term(intent_name), tb.has_component_threshold, Literal(1.0)))
    intent_graph.add((ab.term(intent_name), tb.has_complexity, Literal(1)))


    print("Executing abstract planner")
    start = time.perf_counter()
    scores, algorithms = abstract_planner.get_algorithms_and_implementations_to_solve_task(ontology=ontology, shape_graph=None, intent_graph=intent_graph, data_graph=data_graph)
    end = time.perf_counter()
    ap_time = end - start
    print(f"Execution of abstract planner finished in {ap_time}s")


    pot_impls=[
        cb["implementation-svc"],
        cb["implementation-randomforestclassifier"],]


    print("Executing logical planner")
    start = time.perf_counter()
    logical_plans = logical_planner.generate_logical_plans(ontology=ontology, shape_graph=None, intent_graph = intent_graph, data_graph=data_graph, pot_impls=pot_impls)
    end = time.perf_counter()
    lp_time = end - start
    print(f"Execution of logical planner finished in {lp_time}s")
    

    plan = logical_plans['logical_plans'][0]
    lastplan = logical_plans['logical_plans'][-1]

    first_logical_plan = {
        plan['name']: (plan['plan'], plan['cols']),
        lastplan['name']: (lastplan['plan'], lastplan['cols'])
    }

    logical_plans_dict = {
        lp['name']: (lp['plan'], lp['cols']) for lp in logical_plans['logical_plans']
    }


    print("Executing workflow builder")
    start = time.perf_counter()
    workflows = workflow_builder.generate_workflows(ontology=ontology, intent_graph=intent_graph, data_graph=data_graph, logical_plans=first_logical_plan)
    end = time.perf_counter()
    wb_time = end - start
    print(f"Execution of workflow builder finished in {wb_time}s")


    for name,graph in workflows.items():
        graph.serialize(destination=f'./autoOntology/workflows/{name}.ttl', format='ttl')


    workflow_path = Path('./autoOntology/workflows')
    script_path = Path('./autoOntology/scripts/')

    print("Executing python translator")
    start = time.perf_counter()
    python_pipeline_translator.translate_graph_folder(ontology=ontology, source_folder=workflow_path, destination_folder=script_path)
    end = time.perf_counter()
    tr_time = end - start
    print(f"Execution of translator in {tr_time}s")

    #Clear out workflow directory for next iteration
    for workflow in workflow_path.iterdir():
        workflow.unlink()

    env_python = r"C:\Users\Adria.Portatil-Adria\Documents\uni\PSR\Codi\Intents2Workflows\.venv\Scripts\python.exe"  # Windows

    with open(f"./autoOntology/stats/{task_id}_{data.name}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'accuracy', 'auc', 'logloss', 'annotator_time', 'abstract_planner_time', 'logical_planner_time', 'workflow_builder_time', 'translator_time', 'execution_time', 'plan'])


        
    for script in script_path.iterdir():
        print("Executing", script.stem)
        start = time.perf_counter()
        result = subprocess.run([env_python, script.absolute()])
        end = time.perf_counter()
        ex_time = end - start
        print(f"Execution of script in {ex_time}s")
        
        with open(f"./autoOntology/stats/{task_id}_{data.name}.csv", "a", newline="") as f:
            writer = csv.writer(f)
            
            if result.returncode != 0:
                print("Execution failed")
                writer.writerow([script.stem, -1, -1, -1, an_time, ap_time, lp_time, wb_time, tr_time, ex_time, str(get_component_plan(workflows[script.stem]))])
            else:
                with open('./stats.json', mode = 'r') as f:
                    plan_stats = json.load(f)
                writer.writerow([script.stem, plan_stats['accuracy'], plan_stats['AUC'], plan_stats['logloss'], an_time, ap_time, lp_time, wb_time, tr_time, ex_time, str(get_component_plan(workflows[script.stem]))])
        script.unlink()
    
    if i >= 6:
        break




    # #print(X, y, categorical_indicator, attribute_names)
    # evals = evaluations.list_evaluations(
    # function="area_under_roc_curve",
    # tasks=[task_id])

    # result = pd.DataFrame([
    # {"run_id": v.run_id, "value": v.value}
    # for v in evals.values()
    # ])
    # print("RUNS",len(evals))

    # if len(evals) > 0:
    #     print(result.sort_values("value", ascending=False).head())

