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


def load_graph():

    current_dir = os.path.dirname(os.path.abspath(__file__))
    ontology_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.ttl")
    file_path = os.path.normpath(ontology_path)

    g = Graph()
    g.parse(file_path, format='ttl')

    return g

def store_graph(graph):

    current_dir = os.path.dirname(os.path.abspath(__file__))
    ontology_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.ttl")
    file_path = os.path.normpath(ontology_path)

    graph.serialize(destination=file_path, format='ttl')



def execute_sparql_query(graph, query):
    
    try:
        results = graph.query(query)

        return results
        
    except requests.exceptions.RequestException as e:
        # Log the exception details and re-raise it
        print(f"Failed to execute SPARQL query. Error: {str(e)}")
        raise

def get_intent(user, dataset):
    """
    Retrieves the most used intent associated with a user and dataset.
    
    Args:
    - user (str): The user identifier.
    - dataset (str): The dataset identifier.
    
    Returns:
    - str: The most used intent.
    """
    
    graph = load_graph()
    found = False
    intent = None
    
    # Check if the user has used the dataset before
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <http://localhost/8080/intentOntology#>

    SELECT ?intent (COUNT(?intent) AS ?count)
    WHERE {{
        ml:{user} ml:runs ?workflow.
        ?workflow ml:hasInput ml:{dataset}.
        ?workflow ml:achieves ?task.
        ?task ml:hasIntent ?intent 
    }}
    GROUP BY ?intent
    ORDER BY DESC(?count)
    LIMIT 1
    """
    
    results = execute_sparql_query(graph, query)
    
    if results:
        for row in results:
            intent = row.intent
            found = True
    
    # If not found, look for the dataset usage by any user
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT ?intent (COUNT(?intent) AS ?count)
        WHERE {{
            ?workflow ml:hasInput ml:{dataset}.
            ?workflow ml:achieves ?task.
            ?task ml:hasIntent ?intent 
        }}
        GROUP BY ?intent
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
    
        if results:
            for row in results:
                intent = row.intent
                found = True
    
    # If still not found, look for the most used intent by the user
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT ?intent (COUNT(?intent) AS ?count)
        WHERE {{
            ml:{user} ml:runs ?workflow.
            ?workflow ml:achieves ?task.
            ?task ml:hasIntent ?intent 
        }}
        GROUP BY ?intent
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
    
        if results:
            for row in results:
                intent = row.intent
                found = True
    
    # If still not found, get the most used intent overall
    if not found:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT ?intent (COUNT(?intent) AS ?count)
        WHERE {
            ?task ml:hasIntent ?intent 
        }
        GROUP BY ?intent
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
    
        if results:
            for row in results:
                intent = row.intent
                found = True
    
    return intent.split("#")[-1]

def get_metric(user, dataset, intent):
    """
    Retrieves the most used metric associated with a user, dataset, and intent.
    
    Args:
    - user (str): The user identifier.
    - dataset (str): The dataset identifier.
    - intent (str): The intent identifier.
    
    Returns:
    - str: The most used metric.
    """
    graph = load_graph()
    found = False
    metric = None
    
    # Check if the user has used the dataset for the intent
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <http://localhost/8080/intentOntology#>

    SELECT ?metric (COUNT(?metric) AS ?count)
    WHERE {{
        ml:{user} ml:runs ?workflow.
        ?workflow ml:hasInput ml:{dataset}.
        ?workflow ml:achieves ?task.
        ?task ml:hasIntent ml:{intent}.
        ?task ml:hasRequirement ?eval.
        ?eval ml:onMetric ?metric 
    }}
    GROUP BY ?metric
    ORDER BY DESC(?count)
    LIMIT 1
    """
    
    results = execute_sparql_query(graph, query)
    
    if results:
        for row in results:
            metric = row.metric
            found = True
    
    # If not found, look for the dataset usage by any user for the intent
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT ?metric (COUNT(?metric) AS ?count)
        WHERE {{
            ?workflow ml:hasInput ml:{dataset}.
            ?workflow ml:achieves ?task.
            ?task ml:hasIntent ml:{intent}.
            ?task ml:hasRequirement ?eval.
            ?eval ml:onMetric ?metric 
        }}
        GROUP BY ?metric
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)

        if results:
            for row in results:
                metric = row.metric
                found = True
    
    # If still not found, look for the most used metric by the user for the intent
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT ?metric (COUNT(?metric) AS ?count)
        WHERE {{
            ml:{user} ml:runs ?workflow.
            ?workflow ml:achieves ?task.
            ?task ml:hasIntent ml:{intent}.
            ?task ml:hasRequirement ?eval.
            ?eval ml:onMetric ?metric 
        }}
        GROUP BY ?metric
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)

        if results:
            for row in results:
                metric = row.metric
                found = True
    
    # If still not found, get the most used metric overall for the intent
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT ?metric (COUNT(?metric) AS ?count)
        WHERE {{
            ?task ml:hasIntent ml:{intent}.
            ?task ml:hasRequirement ?eval.
            ?eval ml:onMetric ?metric 
        }}
        GROUP BY ?metric
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                metric = row.metric
                found = True
    
    return metric.split("#")[-1]


def get_preprocessing(user, dataset, intent):
    """
    Determines if preprocessing is required based on user-specific or general task constraints for a given dataset and intent.

    Args:
    - user (str): The user identifier.
    - dataset (str): The dataset identifier.
    - intent (str): The intent identifier.

    Returns:
    - bool: True if preprocessing is required, False otherwise.
    """

    graph = load_graph()
    found = False
    preprocessing = True

    # Check if the user has used the dataset for the intent with ConstraintNoPreprocessing
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <http://localhost/8080/intentOntology#>

    SELECT (COUNT(DISTINCT ?task) AS ?constraintTaskCount)
    WHERE {{
        ml:{user} ml:runs ?workflow.
        ?workflow ml:hasInput ml:{dataset}.
        ?workflow ml:achieves ?task.
        ?task ml:hasIntent ml:{intent}.
        ?task ml:hasConstraint ml:ConstraintNoPreprocessing
    }}
    """
    results = execute_sparql_query(graph, query)
    if results:
        for row in results:
            constraint_task = int(row.constraintTaskCount)
            found = True

    if found:
        # Count total tasks achieved by the user with the dataset
        query_aux = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT (COUNT(DISTINCT ?task) AS ?taskCount)
        WHERE {{
            ml:{user} ml:runs ?workflow.
            ?workflow ml:hasInput ml:{dataset}.
            ?workflow ml:achieves ?task.
        }}
        """
        results = execute_sparql_query(graph, query_aux)
        if results:
            for row in results:
                total_tasks = int(row.taskCount)
                found = True

            if total_tasks > 0:
                if constraint_task / total_tasks < 0.5:
                    preprocessing = True
                else:
                    preprocessing = False

    if not found:
        # Count total tasks achieved by any user with the dataset
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT (COUNT(DISTINCT ?task) AS ?constraintTaskCount)
        WHERE {{
            ?workflow ml:hasInput ml:{dataset}.
            ?workflow ml:achieves ?task.
            ?task ml:hasConstraint ml:ConstraintNoPreprocessing
        }}
        """

        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                constraint_task = int(row.constraintTaskCount)
                found = True

        if found:
            query_aux = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ml: <http://localhost/8080/intentOntology#>

            SELECT (COUNT(DISTINCT ?task) AS ?taskCount)
            WHERE {{
                ?workflow ml:hasInput ml:{dataset}.
                ?workflow ml:achieves ?task.
            }}
            """
            results = execute_sparql_query(graph, query_aux)
            if results:
                for row in results:
                    total_tasks = int(row.taskCount)
                    found = True

                # Check if total_tasks is not zero to avoid division by zero
                if total_tasks > 0:
                    if constraint_task / total_tasks < 0.5:
                        preprocessing = True
                    else:
                        preprocessing = False

    if not found:
        # Count tasks achieved by the user with the intent and ConstraintNoPreprocessing
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT (COUNT(DISTINCT ?task) AS ?constraintTaskCount)
        WHERE {{
            ml:{user} ml:runs ?workflow.
            ?workflow ml:achieves ?task.
            ?task ml:hasIntent ml:{intent}.
            ?task ml:hasConstraint ml:ConstraintNoPreprocessing
        }}
        """
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                constraint_task = int(row.constraintTaskCount)
                found = True

        if found:
            query_aux = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ml: <http://localhost/8080/intentOntology#>

            SELECT (COUNT(DISTINCT ?task) AS ?taskCount)
            WHERE {{
                ml:{user} ml:runs ?workflow.
                ?workflow ml:achieves ?task.
                ?task ml:hasIntent ml:{intent}
            }}
            """
            results = execute_sparql_query(graph, query_aux)
            if results:
                for row in results:
                    total_tasks = int(row.taskCount)
                    found = True

                # Check if total_tasks is not zero to avoid division by zero
                if total_tasks > 0:
                    if constraint_task / total_tasks < 0.5:
                        preprocessing = True
                    else:
                        preprocessing = False

    if not found:
        # Count tasks achieved by any user with the intent and ConstraintNoPreprocessing
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT (COUNT(DISTINCT ?task) AS ?constraintTaskCount)
        WHERE {{
            ?task ml:hasIntent ml:{intent}.
            ?task ml:hasConstraint ml:ConstraintNoPreprocessing
        }}
        """
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                constraint_task = int(row.constraintTaskCount)
                found = True

        if found:
            query_aux = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ml: <http://localhost/8080/intentOntology#>

            SELECT (COUNT(DISTINCT ?task) AS ?taskCount)
            WHERE {{
                ?task ml:hasIntent ml:{intent}
            }}
            """
            results = execute_sparql_query(graph, query_aux)
            if results:
                for row in results:
                    total_tasks = int(row.taskCount)
                    found = True

                # Check if total_tasks is not zero to avoid division by zero
                if total_tasks > 0:
                    if constraint_task / total_tasks < 0.5:
                        preprocessing = True
                    else:
                        preprocessing = False
    if preprocessing:
        return "Yes"
    else:
        return "No"


def get_algorithm(user, dataset, intent):

    """
    Retrieves the most frequently used algorithm for a given user, dataset, and intent.

    Args:
    - user (str): The user identifier.
    - dataset (str): The dataset identifier.
    - intent (str): The intent identifier.

    Returns:
    - str: The most frequently used algorithm for the specified criteria, or None if no algorithm is found.
    """

    graph = load_graph()
    found = False
    algorithm = None
    
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
            algorithm = row.algorithm
            found = True
    
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
                algorithm = row.algorithm
                found = True
    
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
                algorithm = row.algorithm
                found = True
    
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
                algorithm = row.algorithm
                found = True
    
    return algorithm.split("#")[-1] if algorithm else None


def get_preprocessing_algorithm(user, dataset, intent):
    """
    Retrieves the most used preprocessing algorithm associated with a user, dataset, and intent.
    
    Args:
    - user (str): The user identifier.
    - dataset (str): The dataset identifier.
    - intent (str): The intent identifier.
    
    Returns:
    - str: The most used preprocessing algorithm.
    """
    
    graph = load_graph()
    found = False
    algorithm = None
    
    # Check if the user has used the dataset with a preprocessing algorithm
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <http://localhost/8080/intentOntology#>

    SELECT ?algorithm (COUNT(?algorithm) AS ?count)
    WHERE {{
        ml:{user} ml:runs ?workflow.
        ?workflow ml:hasInput ml:{dataset}.
        ?workflow ml:achieves ?task.
        ?task ml:hasConstraint ?constraint.
        ?constraint rdf:type ml:ConstraintPreprocessingAlgorithm.
        ?constraint ml:on ?algorithm 
    }}
    GROUP BY ?algorithm
    ORDER BY DESC(?count)
    LIMIT 1
    """
    
    results = execute_sparql_query(graph, query)
    if results:
        for row in results:
            algorithm = row.algorithm
            found = True
    
    # If not found, look for the dataset usage by any user with a preprocessing algorithm
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT ?algorithm (COUNT(?algorithm) AS ?count)
        WHERE {{
            ?workflow ml:hasInput ml:{dataset}.
            ?workflow ml:achieves ?task.
            ?task ml:hasConstraint ?constraint.
            ?constraint rdf:type ml:ConstraintPreprocessingAlgorithm.
            ?constraint ml:on ?algorithm 
        }}
        GROUP BY ?algorithm
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                algorithm = row.algorithm
                found = True
    
    # If still not found, look for the user's usages of the same intent with a preprocessing algorithm
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
            ?constraint rdf:type ml:ConstraintPreprocessingAlgorithm.
            ?constraint ml:on ?algorithm 
        }}
        GROUP BY ?algorithm
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                algorithm = row.algorithm
                found = True
    
    # If still not found, get the most used preprocessing algorithm overall for the intent
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <http://localhost/8080/intentOntology#>

        SELECT ?algorithm (COUNT(?algorithm) AS ?count)
        WHERE {{
            ?task ml:hasIntent ml:{intent}.
            ?task ml:hasConstraint ?constraint.
            ?constraint rdf:type ml:ConstraintPreprocessingAlgorithm.
            ?constraint ml:on ?algorithm 
        }}
        GROUP BY ?algorithm
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                algorithm = row.algorithm
                found = True    
    
    return algorithm.split("#")[-1]


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



def add_new_workflow(data):
    """
    Adds a new workflow to the GraphDB repository using the provided data and returns the workflow's name.

    Args:
    - data (dict): The data required to create and add the new workflow.

    Returns:
    - str: The name of the added workflow if successful, or None if there was an error.
    """
    repository_id = repository
    url = f"http://localhost:8080/repositories/{repository_id}/statements"

    headers = {
        "Content-Type": "application/sparql-update"
    }

    insert_query, workflow_uri, user_uri, workflow_name = save_workflow.generate_sparql_insert_query(data)

    response = requests.post(url, headers=headers, data=insert_query)

    if response.status_code == 204:
        print(f"Added new workflow: {workflow_uri} for the user {user_uri}")
        return workflow_name
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


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