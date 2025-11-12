from typing import List, Set, Type
from rdflib import Graph, URIRef, Literal
from common import *

def get_dataset_type(data_graph: Graph, dataset:URIRef):
    return next(data_graph.objects(dataset, RDF.type),Literal("")).toPython()

def get_dataset_format(data_graph: Graph, dataset:URIRef):
    return next(data_graph.objects(dataset, dmop.fileFormat,unique=True),Literal("")).toPython()

def get_dataset_path(data_graph: Graph, dataset:URIRef):
    return next(data_graph.objects(dataset, dmop.path, unique=True),Literal("")).toPython()

def get_dataset_uri(data_graph: Graph) -> URIRef:
    data_uri_query = f"""
PREFIX tb: <{tb}>
SELECT ?uri
WHERE {{
    ?uri a tb:Dataset .
}}
"""
    result = data_graph.query(data_uri_query).bindings
    assert len(result) == 1
    return result[0]['uri']


def get_dataset_feature_types(data_graph: Graph, dataset: URIRef) -> Set[Type]:
    columns_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?type
        WHERE {{
            {dataset.n3()} dmop:hasColumn ?column .
            ?column dmop:isFeature true ;
                    dmop:hasDataPrimitiveTypeColumn ?type .
        }}
    """
    columns = data_graph.query(columns_query).bindings
    mapping = {
        dmop.Float: float,
        dmop.Int: int,
        dmop.Integer: int,
        dmop.Number: float,
        dmop.Double: float,
        dmop.String: str,
        dmop.Boolean: bool,
    }
    return set([mapping[x['type']] for x in columns])

def get_datset_label_name(data_graph: Graph, dataset:URIRef) -> str:
    label_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {dataset.n3()} dmop:hasColumn ?column .
            ?column dmop:isLabel true ;
                    dmop:hasColumnName ?label .

        }}
    """
    
    results = data_graph.query(label_query).bindings
    
    if results is not None and len(results) > 0:
        return results[0]['label']
    
    return ""


def get_dataset_numeric_columns(data_graph: Graph, dataset:URIRef) -> List[str]:

    columns_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {dataset.n3()} dmop:hasColumn ?column .
            ?column dmop:isFeature true ;
                    dmop:hasDataPrimitiveTypeColumn ?type ;
                    dmop:hasColumnName ?label .
            FILTER(?type IN (dmop:Float, dmop:Int, dmop:Number, dmop:Double, dmop:Long, dmop:Short, dmop:Integer))
        }}
    """
    columns = data_graph.query(columns_query).bindings
 
    return [x['label'].value for x in columns]


def get_dataset_categorical_columns(data_graph: Graph, dataset: Graph) -> List[str]:
    categ_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {dataset.n3()} dmop:hasColumn ?column .
            ?column dmop:isCategorical true ;
                    dmop:hasDataPrimitiveTypeColumn ?type ;
                    dmop:isFeature true ;
                    dmop:hasColumnName ?label .
        }}
    """
    columns = data_graph.query(categ_query).bindings

    return [x['label'].value for x in columns]

def get_dataset_target_column(data_graph: Graph, dataset: Graph) -> str:
    label_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {dataset.n3()} dmop:hasColumn ?column .
            ?column dmop:isLabel true ;
                    dmop:hasColumnName ?label .
        }}
    """
    columns = data_graph.query(label_query).bindings

    if len(columns) == 1:
        return columns[0]['label'].value 
    else:
        print("WARNING: unusal target column resoinse:", list(columns))
        return ""

def get_dataset_columns(data_graph:Graph, dataset:Graph)-> List[str]:
    query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {dataset.n3()} dmop:hasColumn ?column .
            ?column dmop:hasColumnName ?label .
        }}
        """
    columns = data_graph.query(query).bindings

    return [x['label'].value for x in columns]