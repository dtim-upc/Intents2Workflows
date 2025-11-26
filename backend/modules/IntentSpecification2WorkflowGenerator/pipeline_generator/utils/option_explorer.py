from rdflib import Graph
import requests
import json

from graph_queries.intent_queries import get_intent_iri, get_intent_dataset_task
from common import tb, RDF, cb


OPTION_EXPLORER_URL = "http://194.249.3.27:8000/experiment/call_mdp"


mappings = {
    'RNN': cb.NN,
    'CNN': cb.NN
}


def get_best_options(intent_graph:Graph, ontology:Graph):
    
    intent_iri = get_intent_iri(intent_graph)
    dataset, task, algorithm = get_intent_dataset_task(intent_graph, intent_iri)

    exp_constraints = intent_graph.objects(intent_iri,tb.hasConstraint)

    intent_graph.serialize("intnenttest.ttl", format="turtle")

    soft_constraints = []
    for constraint in exp_constraints:
        print(constraint)
        value_node = next(intent_graph.objects(constraint, tb.hasConstraintValue, unique=True))
        print(value_node)
        name = next(ontology.objects(constraint, tb.hasOptionExplorerName, unique=True))
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
        'algorithm': algorithm.fragment if algorithm is not None else None,
        'method': None, #task.fragment if task is not None else None,
        "hard_constraints": [],
        "soft_constraints": [
            c for c in soft_constraints
        ]
    }

    print(json_data)

    headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDE1Njc4OSwianRpIjoiZDkzMDgxNjMtMjBkYi00NGI0LWEzNzMtOGE0MjRmYTk0MDYyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IntcInVzZXJfaWRcIjogMSwgXCJuYW1lXCI6IFwiTW9oYW1tYWRcIiwgXCJsYXN0X25hbWVcIjogXCJQZXplc2hraVwiLCBcInByb2ZpbGVfcGljXCI6IG51bGwsIFwiZW1haWxcIjogXCJtb2hhbW1hZEBnbWFpbC5jb21cIiwgXCJhZGRyZXNzXCI6IFwiVmlhIFNhbiBNYXJjb1wiLCBcImJpcnRoX2RhdGVcIjogXCIxOTk0LTEyLTAzXCIsIFwic3RhdHVzXCI6IFwiYWN0aXZlXCIsIFwiY3JlYXRpb25fZGF0ZVwiOiBcIjIwMjUtMTEtMjZUMTE6Mjk6NTQuMjg0MTg1XCIsIFwiZWR1Y2F0aW9uYWxfbGV2ZWxcIjogXCJCYWNoZWxvcidzIERlZ3JlZVwiLCBcImVkdWNhdGlvbmFsX2ZpZWxkXCI6IFwiQ29tcHV0ZXIgU2NpZW5jZVwifSIsIm5iZiI6MTc2NDE1Njc4OSwiY3NyZiI6ImM2NzU1YjdlLWJmNzgtNDFiZC1iYjFjLWZhM2ViYmMxOWFmMiIsImV4cCI6MTc2NDI0MzE4OX0.0VA5jVSKOlwq3YyntGYaW4BPXP2bgR6KVgbI6uyu7YI" # This is not exaclty good parctice, but it is enough for now
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
            if not translated_alg is None:
                algs[translated_alg] = exp['utility_value']
        
        return algs


    else:
        print(f"Request option explorer failed with status code {response.status_code}")
        print(response.text) 

