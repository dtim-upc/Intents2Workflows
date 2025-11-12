from rdflib import Graph
import requests
import json

from pipeline_generator.graph_queries import get_intent_iri, get_intent_dataset_task
from common import tb, RDF


OPTION_EXPLORER_URL = "http://194.249.3.27:8000/experiment/call_mdp"


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
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDMzNDEzNCwianRpIjoiYzI0MGU1MTUtNDVlZS00ZTY1LWE3MTktZjE4YTg4MTU3MWNmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IntcInVzZXJfaWRcIjogMSwgXCJuYW1lXCI6IFwiTW9oYW1tYWRcIiwgXCJsYXN0X25hbWVcIjogXCJQZXplc2hraVwiLCBcInByb2ZpbGVfcGljXCI6IG51bGwsIFwiZW1haWxcIjogXCJtb2hhbW1hZEBnbWFpbC5jb21cIiwgXCJhZGRyZXNzXCI6IFwiVmlhIFNhbiBtYXJjb1wiLCBcImJpcnRoX2RhdGVcIjogXCIxOTk0LTAzLTEyXCIsIFwic3RhdHVzXCI6IFwiYWN0aXZlXCIsIFwiY3JlYXRpb25fZGF0ZVwiOiBcIjIwMjUtMDMtMTRUMTE6NDQ6MzYuNzA5NTc5XCIsIFwiZWR1Y2F0aW9uYWxfbGV2ZWxcIjogXCJcIiwgXCJlZHVjYXRpb25hbF9maWVsZFwiOiBcIlwifSIsIm5iZiI6MTc1MDMzNDEzNCwiY3NyZiI6IjE5OGYzODNmLWFmMDEtNGQ3ZC05NTIzLTA1YTBiNDVlNzJlMCIsImV4cCI6MTc1MDQyMDUzNH0.6afv6PuD8Cw8CXNlASKOwnclZ1ZzEFcEvr0FdBrabO0" # This is not exaclty good parctice, but it is enough for now
    }


    # Making the POST request
    response = requests.post(OPTION_EXPLORER_URL, json=json_data, headers=headers)

    # Check the response
    if response.status_code == 200:
        print("Success! Response data:")
        print(response.json())

        resp = response.json()
        algs = []
        for exp in resp['data']:
            algs.append((exp['utility_value'], exp['algorithm']))
        
        return algs


    else:
        print(f"Request option explorer failed with status code {response.status_code}")
        print(response.text) 

