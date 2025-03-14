import requests
import urllib.parse
import json
import pandas as pd
import rdflib
from rdflib import Graph, URIRef, XSD, Literal, Namespace
from rdflib.namespace import RDF, RDFS
import math
import os
from utils import save_workflow


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

def store_graph(graph, format = 'tsv'):

    if format == 'ttl':
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ontology_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.ttl")
        file_path = os.path.normpath(ontology_path)

        graph.serialize(destination=file_path, format='ttl')
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ontology_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.tsv")
        file_path = os.path.normpath(ontology_path)
        tsv_data = []
        for subj, pred, obj in graph:
            tsv_data.append((subj, pred, obj))
        df = pd.DataFrame(tsv_data)
        df.to_csv(file_path, sep="\t", index=False, header=False)



def execute_sparql_query(graph, query):
    
    try:
        results = graph.query(query)

        return results
        
    except requests.exceptions.RequestException as e:
        # Log the exception details and re-raise it
        print(f"Failed to execute SPARQL query. Error: {str(e)}")
        raise


def get_users_with_workflows():

    """
    Retrieves a list of distinct users who have associated workflows.

    Returns:
    - list of str: User identifiers (names) who have at least one workflow.
    """
    graph = load_graph()
    query = """
    PREFIX ml: <http://localhost/8080/intentOntology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?user
    WHERE {
      ?user ml:runs ?workflow .
    }
    """

    results = execute_sparql_query(graph, query)
    users = []
    if results:
        for row in results:
            users.append(row.user.split('#')[-1])
    
    return users


def get_users():
    """
    Retrieves a list of distinct users from the repository.

    Returns:
    - list of str: User identifiers (names) for all users of type `ml:User`.
    """
    global last_inserted_user  # Declare the use of the global variable
    
    graph = load_graph()
    query = """
    PREFIX ml: <http://localhost/8080/intentOntology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?user
    WHERE {
    ?user rdf:type ml:User .
    }
    """
    results = execute_sparql_query(graph, query)
    users = []
    if results:
        for row in results:
            users.append(row.user.split('#')[-1])


    # Extract numeric part and find the highest number
    user_numbers = []
    for user in users:
        if user.startswith("User"):
            num_part = user[4:] 
            user_numbers.append(int(num_part))
    
    next_user_number = max(user_numbers) if user_numbers else 0
    new_user = f"User{next_user_number}"

    last_inserted_user = new_user
    
    return {
        "users": users,
        "last_inserted_user": last_inserted_user
    }

def add_new_user(email):
    """
    Adds a new user with a unique ID and specified email to the GraphDB repository and updates the last inserted user record.

    Args:
    - email (str): The email address of the new user.

    Returns:
    - str: The ID of the newly added user if successful, or None if there was an error.
    """
    result = get_users()  # Call the updated get_users function
    last_inserted_user = result["last_inserted_user"]   

    # print(last_inserted_user)
    numeric_part = ''.join(filter(str.isdigit, last_inserted_user))
    new_user_id = f"User{int(numeric_part) + 1}"

    ML = Namespace("http://localhost/8080/intentOntology#")

    # Add triples manually
    graph = load_graph()
    graph.add((URIRef(ML[new_user_id]), RDF.type, URIRef(ML.User)))
    graph.add((URIRef(ML[new_user_id]), URIRef(ML.email), Literal(email)))

    last_inserted_user = new_user_id
    store_graph(graph)

    return new_user_id


def find_user_by_email(email):
    """
    Retrieves the user ID associated with the specified email address.

    Args:
    - email (str): The email address of the user to find.

    Returns:
    - str: The user ID if a user with the specified email is found, or None if no such user exists.
    """
    graph = load_graph()
    query = f"""
    PREFIX ml: <http://localhost/8080/intentOntology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?user
    WHERE {{
        ?user rdf:type ml:User .
        ?user ml:email "{email}" .
    }}
    """

    results = execute_sparql_query(graph, query)
    if results:
        for row in results:
            return row.user.split('#')[-1]
    
    return None


def add_new_dataset(dataset_name):
    """
    Adds a new dataset with the specified name to the repository.

    Args:
    - dataset_name (str): The name of the dataset to be added.

    Returns:
    - str: The name of the added dataset if successful, or None if there was an error.
    """
    dataset_uri = f"http://localhost/8080/intentOntology#{dataset_name}"

    query = f"""
    PREFIX ns_dmop: <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#>
    PREFIX RDF: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    INSERT DATA {{
        <{dataset_uri}> RDF:type ns_dmop:DataSet .
    }}
    """
    graph = load_graph()
    NS_DMOP = Namespace("http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#")
    graph.add((URIRef(dataset_uri), RDF.type, URIRef(NS_DMOP.DataSet)))
    store_graph(graph)

    return dataset_name


def get_all_metrics():
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <http://localhost/8080/intentOntology#>
    
    SELECT DISTINCT ?object
    WHERE {{
      ?subject ml:specifies ?object .
    }}
    ORDER BY ASC(?object)
    """
    graph = load_graph()
    results = execute_sparql_query(graph, query)
    metrics = []
    if results:
        for row in results:
            metrics.append(row.object.split('#')[-1])

    return metrics


def get_all_algorithms():
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <http://localhost/8080/intentOntology#>
    
    
    SELECT DISTINCT ?algorithm
    WHERE {{
            ?algorithm a <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#ClassificationModelingAlgorithm>
        }}
    ORDER BY ASC(?algorithm)
    """

    graph = load_graph()
    results = execute_sparql_query(graph, query)
    algorithms = []
    if results:
        for row in results:
            algorithms.append(row.algorithm.split('#')[-1])

    return algorithms


def get_all_preprocessing_algorithms():
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <http://localhost/8080/intentOntology#>
    
    
    SELECT DISTINCT ?algorithm
    WHERE {{
            ?algorithm a <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#DataProcessingAlgorithm>
        }}
    ORDER BY ASC(?algorithm)
    """

    graph = load_graph()
    results = execute_sparql_query(graph, query)
    preprocessing_algorithms = []
    if results:
        for row in results:
            preprocessing_algorithms.append(row.algorithm.split('#')[-1])

    return preprocessing_algorithms