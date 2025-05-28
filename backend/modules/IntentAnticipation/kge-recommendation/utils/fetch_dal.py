import requests
import uuid
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

def parse_iso(timestamp):
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '..','..','..','..', '.env')
load_dotenv(dotenv_path=env_path)



def update_graph():
    '''
    Access the Data Abstraction Layer (DAL) to initialize the KG with the stored data. Currently
    it is not an incremental solution.
    '''

    # Read token:
    token = os.getenv("DAL_TOKEN")
    if token == None:
        return
    last_processed_str = os.getenv("LAST_PROCESSED")
    if last_processed_str:
        last_processed = parse_iso(last_processed_str)
    else:
        last_processed = parse_iso("2023-05-28T08:27:18Z")
    
    name_space = 'https://extremexp.eu/ontology#'
    triples = []

    url = "https://api.expvis.smartarch.cz/api/workflows"
    headers = {"access-token": token}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return
    
    for workflow in data['workflows']:
        for id in workflow:
            if workflow[id]['status'] == 'completed':
                if 'end' in workflow[id].keys():
                    end = parse_iso(workflow[id]['end'])
                    if end > last_processed:

                        if 'user' in workflow[id].keys():
                            triples.append((name_space+workflow[id]['user'], name_space+ 'specifies', name_space+id))

                        if 'input_datasets' in workflow[id].keys():
                            for dataset in workflow[id]['input_datasets']:
                                    triples.append((name_space+id, name_space+ 'hasDataset', name_space+dataset['name']))
                        
                        if 'intent' in workflow[id].keys():
                            triples.append((name_space+id, name_space+ 'hasIntent', name_space+workflow[id]['intent']))

                        if 'tasks' in workflow[id].keys():
                            final = workflow[id]['tasks'][-1] #TODO Change Accordingly
                            triples.append((name_space+id, name_space+ 'hasAlgorithm', name_space+final['name']))
                        
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


    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '..','..','..','..', '.env')

    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(env_path, "r") as f:
        lines = f.readlines()

    with open(env_path, "w") as f:
        updated = False
        for line in lines:
            if line.startswith("LAST_PROCESSED="):
                f.write(f"LAST_PROCESSED={now_iso}\n")
                updated = True
            else:
                f.write(line)
        if not updated:
            f.write(f"LAST_PROCESSED={now_iso}\n")        

            
            

            


