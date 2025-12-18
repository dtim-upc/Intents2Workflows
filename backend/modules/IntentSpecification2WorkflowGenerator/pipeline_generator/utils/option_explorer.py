import random
from rdflib import Graph
import requests
import json

from graph_queries.intent_queries import get_intent_iri, get_intent_dataset_task
from common import tb, RDF, cb, RDFS


OPTION_EXPLORER_URL = "http://194.249.3.27:8000/experiment/call_mdp"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDY4NjE0MSwianRpIjoiYzA3YjQxNzItYTQ1Zi00MzEyLTk0YWQtZDIwYTE0M2IxODZiIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IntcInVzZXJfaWRcIjogMSwgXCJuYW1lXCI6IFwiTW9oYW1tYWRcIiwgXCJsYXN0X25hbWVcIjogXCJQZXplc2hraVwiLCBcInByb2ZpbGVfcGljXCI6IG51bGwsIFwiZW1haWxcIjogXCJtb2hhbW1hZEBnbWFpbC5jb21cIiwgXCJhZGRyZXNzXCI6IFwiVmlhIFNhbiBNYXJjb1wiLCBcImJpcnRoX2RhdGVcIjogXCIxOTk0LTEyLTAzXCIsIFwic3RhdHVzXCI6IFwiYWN0aXZlXCIsIFwiY3JlYXRpb25fZGF0ZVwiOiBcIjIwMjUtMTEtMzBUMTk6Mzk6MjIuNjg5Mzc2XCIsIFwiZWR1Y2F0aW9uYWxfbGV2ZWxcIjogXCJCYWNoZWxvcidzIERlZ3JlZVwiLCBcImVkdWNhdGlvbmFsX2ZpZWxkXCI6IFwiQ29tcHV0ZXIgU2NpZW5jZVwifSIsIm5iZiI6MTc2NDY4NjE0MSwiY3NyZiI6IjI5Mjk2MTU0LTRlMTEtNDJjOS04ZmUzLWRjMWRkODMxNzEwNyIsImV4cCI6MTc2NDc3MjU0MX0.4G9gfqI0c50WwGNo2kF79Uv0AilUgr7NBQcC4i3qL6U"


mappings = {
    'RNN': cb.NN,
    'CNN': cb.NN,
    'Gradient Boosting': cb.XGBoost,
    'SVM': cb.SVM,
    "Random Forest": cb.DecisionTree
}


def get_best_options(intent_graph:Graph, ontology:Graph):
    
    intent_iri = get_intent_iri(intent_graph)
    dataset, task, algorithm = get_intent_dataset_task(intent_graph, intent_iri)

    exp_constraints = intent_graph.objects(intent_iri,tb.hasConstraint)

    soft_constraints = []
    for constraint in exp_constraints:
        print(constraint)
        value_node = next(intent_graph.objects(constraint, tb.hasConstraintValue, unique=True))
        print(value_node)
        name = next(ontology.objects(constraint, RDFS.label, unique=True))
        print(name)
        value_type = next(intent_graph.objects(value_node, RDF.type, unique=True))
        print(value_type)

        constr = {
            "name": str(name),
        }

        if value_type == tb.LiteralValue:
            literal_value = next(intent_graph.objects(value_node, tb.hasLiteralValue, unique=True), None)
            constr["type"] = "categorical"
            constr["value"] = str(literal_value) if literal_value is not None else None

        else:
            min_value = next(intent_graph.objects(value_node, tb.hasMinValue, unique=True), None)
            max_value = next(intent_graph.objects(value_node, tb.hasMaxValue, unique=True), None)
            constr["type"] = "numerical"
            constr["min"] = float(min_value) if min_value is not None else None
            constr["max"] = float(max_value) if max_value is not None else None
        soft_constraints.append(constr)


    json_data = {
        'domain': "manufacturing",
        'intent': "anomaly detection",
        'algorithm': None,
        'method': None, #task.fragment if task is not None else None,
        "hard_constraints": [],
        "soft_constraints": [
            c for c in soft_constraints
        ]
    }

    print(json_data)
    auth = f"Bearer {TOKEN}" 

    # This is not exaclty good parctice, but it is enough for now
    headers = {
    "Content-Type": "application/json",
    "Authorization": auth
    }

    try:
        # Making the POST request
        response = requests.post(OPTION_EXPLORER_URL, json=json_data, headers=headers)
    
    except Exception as e:
        print("Option explorer connection error:", e)
        return {}



    # Check the response
    if response.status_code == 200:
        print("Success! Response data:")
        print(response.json())

        resp = response.json()
        algs = {}
        for exp in resp.get('data',[]):
            translated_alg = mappings.get(exp['algorithm'],None)
            if not translated_alg is None and \
                (translated_alg not in algs or exp.get('utility_value',0) > algs[translated_alg]['utility_value']):
                
                algs[translated_alg] = {
                    'utility_value': exp.get('utility_value',0),
                    'loss': exp.get("loss",None),
                    'accuracy': exp.get("accuracy",None),
                    'recall':exp.get("recall",None),
                    "precision":exp.get("precision",None),
                    "f1_score":exp.get("f1_score",None),
                    "training_time":exp.get("training_time",None),
                }
        
        return algs


    else:
        print(f"Request option explorer failed with status code {response.status_code}")
        print(response.text) 
    
    return {}

def get_placeholder_metrics():
        return {
                    'utility_value': round(random.random(),3),
                    'loss': round(random.random(),3),
                    'accuracy': round(random.random(),3),
                    'recall':round(random.random(),3),
                    "precision":round(random.random(),3),
                    "f1_score":round(random.random(),3),
                    "training_time":round(random.random(),3),
                }