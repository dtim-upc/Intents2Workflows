from rdflib import Graph, URIRef, XSD, Literal, Namespace
from pykeen.training import SLCWATrainingLoop
from pykeen.triples import TriplesFactory
from rdflib.namespace import RDF, RDFS
from pykeen.models import TransE
from torch.optim import Adam
import urllib.parse
import pandas as pd
import requests
import csv
import time
import rdflib
import os
import pickle
import torch






def annotate_tsv(user,intent,dataset):
    #TODO : HOW ARE USER,INTENT,DATASET PASSED HERE
    current_dir = os.path.dirname(os.path.abspath(__file__))
    new_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "new_triples.tsv")
    new_triples_path = os.path.normpath(new_path)


    experiment = user+intent+dataset + str(time.time()).split('.')[0]

    #TODO ADDAPT TO THE ONTOLOGY: Change name space and relation names
    name_space = 'http://localhost/7200/intentOntology#'
    triples = [
    (name_space+user, name_space+ 'specifies', name_space+experiment), 
    (name_space+experiment, name_space + 'hasIntent', name_space+intent),
    (name_space+experiment, name_space+ 'hasDataset', name_space+dataset)]

    with open(new_triples_path, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerows(triples)
    
    return experiment # Is just experiment what we want?


def load_graph(format = 'tsv'):


    if format == 'ttl':
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ontology_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.ttl")
        file_path = os.path.normpath(ontology_path)

        g = Graph()
        g.parse(file_path, format='ttl')

    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ontology_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.tsv")
        file_path = os.path.normpath(ontology_path)
        df = pd.read_csv(file_path, sep="\t", header=None, dtype=str)
        data = df.values
        g = rdflib.Graph()
        g.addN((rdflib.URIRef(s), rdflib.URIRef(p), rdflib.URIRef(o), g) for s, p, o in data)

    return g

def execute_sparql_query(graph, query):
    
    try:
        results = graph.query(query)

        return results
        
    except requests.exceptions.RequestException as e:
        # Log the exception details and re-raise it
        print(f"Failed to execute SPARQL query. Error: {str(e)}")
        raise


'''
This file will provide the recommendations with explanations, combining SPARQL with KGE
'''

def recommendations(experiment,user,intent,dataset):

    graph = load_graph()
    suggestions = {}
    ################################################################################
    ################################## UPDATE KGE ##################################
    ################################################################################

    seed = 8182
    embedding_dimension = 128
    learning_rate_fine_tune = 0.0001
    num_finetune_epochs = 5
    num_negs_per_pos = 20

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "new_triples.tsv")
    new_triples_path = os.path.normpath(path)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.tsv")
    triples_path = os.path.normpath(path)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


    # LOAD ALL DICTIONARIES AND EMBEDDINGS

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "entity_to_id.pkl")
    norm_path_e2i = os.path.normpath(path)
    with open(norm_path_e2i, "rb") as f:
        old_ent_to_id = pickle.load(f)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "relation_to_id.pkl")
    norm_path_r2i = os.path.normpath(path)
    with open(norm_path_r2i, "rb") as f:
        old_rel_to_id = pickle.load(f)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "entity_representations.pkl")
    norm_path_ee = os.path.normpath(path)
    with open(norm_path_ee, "rb") as f:
        old_ent_emb = pickle.load(f).to(device)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "relation_representations.pkl")
    norm_path_re = os.path.normpath(path)
    with open(norm_path_re, "rb") as f:
        old_rel_emb = pickle.load(f).to(device)

    df1 = pd.read_csv(triples_path, sep="\t", header= None)
    df2 = pd.read_csv(new_triples_path, sep="\t", header=None)
    combined_df = pd.concat([df1, df2], ignore_index=True)
    combined_df.to_csv(triples_path, sep="\t", index=False)

    training_triples_factory = TriplesFactory.from_path(triples_path)

    # Initialize the model with all the entities/relations
    model = TransE(triples_factory=training_triples_factory, embedding_dim=embedding_dimension, random_seed = seed).to(device)

    new_ent_emb = model.entity_representations[0](indices= None).clone().detach().to(device)
    new_rel_emb = model.relation_representations[0](indices= None).clone().detach().to(device)

    # Get new mappings

    new_ent_to_id = training_triples_factory.entity_to_id
    new_rel_to_id = training_triples_factory.relation_to_id

    # Keep the embeddings of old entities/relations
    with torch.no_grad():
        for i in old_ent_to_id:
            old_idx = old_ent_to_id[i]
            new_idx = training_triples_factory.entity_to_id[i]

            old_vector = old_ent_emb[old_idx].to(device)
            new_ent_emb[new_idx] = old_vector

        for j in old_rel_to_id:
            old_idx = old_rel_to_id[j]
            new_idx = training_triples_factory.relation_to_id[j]

            old_vector = old_rel_emb[old_idx].to(device)
            new_rel_emb[new_idx] = old_vector

        model.entity_representations[0]._embeddings.weight.copy_(new_ent_emb)
        model.relation_representations[0]._embeddings.weight.copy_(new_rel_emb)
    
    #TODO Initialization

    model = model.to(device)

    training_triples = TriplesFactory.from_path(new_triples_path, entity_to_id=new_ent_to_id, relation_to_id=new_rel_to_id)

    optimizer = Adam(params=model.get_grad_params(),lr=learning_rate_fine_tune)

    training_loop = SLCWATrainingLoop(model=model,
                                    triples_factory=training_triples,
                                    optimizer=optimizer,
                                    negative_sampler_kwargs = {'num_negs_per_pos':num_negs_per_pos})

    tl = training_loop.train(triples_factory=training_triples,
                            num_epochs=num_finetune_epochs)
    


    with open(norm_path_ee, "wb") as f:
        pickle.dump(model.entity_representations[0](indices= None).clone().detach(), f)

    with open(norm_path_re, "wb") as f:
        pickle.dump(model.relation_representations[0](indices= None).clone().detach(), f)

    with open(norm_path_e2i, "wb") as f:
        pickle.dump(new_ent_to_id, f)

    with open(norm_path_r2i, "wb") as f:
        pickle.dump(new_rel_to_id, f)


    
    ################################################################################
    ################################## ALGORITHM ###################################
    ################################################################################
    
    found = False
    algorithm_sparql = None
    algorithm_sparql_explanation = ''

    # Check if the user has used the dataset with a specific algorithm constraint
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <http://localhost/8080/intentOntology#>

    SELECT ?algorithm (COUNT(?algorithm) AS ?count)
    WHERE {{
        ml:{user} ml:runs ?workflow.
        ?workflow ml:hasInput ml:{dataset}.
        ?workflow ml:achieves ?task.
        ?task ml:hasConstraint ?constraint.
        ?constraint rdf:type ml:ConstraintAlgorithm.
        ?constraint ml:on ?algorithm 
    }}
    GROUP BY ?algorithm
    ORDER BY DESC(?count)
    LIMIT 1
    """
    
    results = execute_sparql_query(graph, query)
    if results:
        for row in results:
            algorithm_sparql = row.algorithm
            found = True
            algorithm_sparql_explanation = 'This is your most frequently used algorithm for this dataset.'
    
    # If not found, look for other users' usage of the dataset
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT ?algorithm (COUNT(?algorithm) AS ?count)
        WHERE {{
            ?workflow ml:hasInput ml:{dataset}.
            ?workflow ml:achieves ?task.
            ?task ml:hasConstraint ?constraint.
            ?constraint rdf:type ml:ConstraintAlgorithm.
            ?constraint ml:on ?algorithm 
        }}
        GROUP BY ?algorithm
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                algorithm_sparql = row.algorithm
                found = True
                algorithm_sparql_explanation = 'This is the most frequently used algorithm for this dataset.'
    
    # If still not found, look for the user's usage of the same intent
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT ?algorithm (COUNT(?algorithm) AS ?count)
        WHERE {{
            ml:{user} ml:runs ?workflow.
            ?workflow ml:achieves ?task.
            ?task ml:hasIntent ml:{intent}.
            ?task ml:hasConstraint ?constraint.
            ?constraint rdf:type ml:ConstraintAlgorithm.
            ?constraint ml:on ?algorithm 
        }}
        GROUP BY ?algorithm
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                algorithm_sparql = row.algorithm
                found = True
                algorithm_sparql_explanation = 'This is your most frequently used algorithm for '+intent+' experiments.'
    
    # If still not found, get the most used algorithm for the intent overall
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT ?algorithm (COUNT(?algorithm) AS ?count)
        WHERE {{
            ?task ml:hasIntent ml:{intent}.
            ?task ml:hasConstraint ?constraint.
            ?constraint rdf:type ml:ConstraintAlgorithm.
            ?constraint ml:on ?algorithm 
        }}
        GROUP BY ?algorithm
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                algorithm_sparql = row.algorithm
                found = True
                algorithm_sparql_explanation = 'This is you most frequently used algorithm for '+intent+' experiments.'
    
    algorithm_sparql = algorithm_sparql.split("#")[-1] if algorithm_sparql else None







    algorithm_kge = None
    algorithm_kge_explanation = 'Similar '+intent + ' experiments have used this algoroithm.'

    #TODO: Replace with a query to get the algorithms complying the intent

    candidate_algorithms = ['http://localhost/8080/intentOntology#sklearn-RandomForestClassifier','http://localhost/8080/intentOntology#sklearn-RandomForestClassifier']


    #TODO Adapt to what we want to predict. Name space to ontology
    name_space = 'http://localhost/7200/intentOntology#'
    relation = name_space + 'achieves'
    head = name_space + experiment

    head_idx = new_ent_to_id[head]
    relation_idx = new_rel_to_id[relation]
    tail_indices = [new_ent_to_id[alg] for alg in candidate_algorithms]

    batch = [[head_idx, relation_idx, tail_idx] for tail_idx in tail_indices]
    batch_tensor = torch.tensor(batch, dtype=torch.long)

    scores = model.predict_hrt(batch_tensor)

    algorithm_scores = {candidate_algorithms[i]: scores[i].item() for i in range(len(candidate_algorithms))}

    algorithm_kge = max(algorithm_scores, key=algorithm_scores.get)

    suggestions['algorithm'] = {'SPARQL': [algorithm_sparql,algorithm_sparql_explanation], 'KGE': [algorithm_kge, algorithm_kge_explanation]}

    return suggestions