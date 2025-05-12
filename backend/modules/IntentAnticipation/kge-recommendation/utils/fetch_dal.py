import requests
import uuid
import csv
import os


def generate_graph():
    '''
    Access the Data Abstraction Layer (DAL) to initialize the KG with the stored data. This
    is not an incremental solution.
    '''

    name_space = 'https://extremexp.eu/ontology#'
    triples = []

    url = "https://api.expvis.smartarch.cz/api/workflows"
    headers = {"access-token": "you_token_here"} #TODO
    response = requests.get(url, headers=headers)
    data = response.json()

    for workflow in data['workflows']:
        for id in workflow:
            if workflow[id]['status'] == 'completed':

                if 'user' in workflow[id].keys():
                    triples.append((name_space+workflow[id]['intent'], name_space+ 'specifies', name_space+id))

                if 'input_datasets' in workflow[id].keys():
                    for dataset in workflow[id]['input_datasets']:
                            triples.append((name_space+id, name_space+ 'hasDataset', name_space+dataset['name']))
                
                if 'intent' in workflow[id].keys():
                    triples.append((name_space+id, name_space+ 'hasIntent', name_space+workflow[id]['intent']))

                if 'tasks' in workflow[id].keys():
                    final = workflow[id]['tasks'][-1] #TODO Change Accordingly
                    triples.append((name_space+id, name_space+ 'hasFeedback', name_space+final['name']))
                
                if 'feedback' in workflow[id].keys():
                    triples.append((name_space+id, name_space+ 'hasFeedback', name_space+workflow[id]['feedback']))
                
                if 'metrics' in workflow[id].keys():
                    for m in workflow[id]['metrics']:
                            metric_id = str(uuid.uuid4())
                            if 'semanticType' in m.keys() and 'values' in m.keys():
                                metric = m['semanticType']
                                metric_value = m['value']
                                triples.append((name_space+metric_id, name_space+ 'onMetric', name_space+metric))
                                triples.append((name_space+metric_id, name_space+ 'onMetric', name_space+metric_value))
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.tsv")
    file_path = os.path.normpath(path)  

    existing_triples = set()

    if os.path.exists(file_path):
        with open(file_path, mode="r", newline="") as file:
            reader = csv.reader(file, delimiter="\t")
            for row in reader:
                existing_triples.add(tuple(row)) 

    for triple in triples:
        existing_triples.add(tuple(triple)) 

    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerows(existing_triples)        

            
            

            


