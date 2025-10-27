from rdflib import Graph, URIRef
from common import *

def get_dataset_type(data_graph: Graph, dataset:URIRef):
    return next(data_graph.objects(dataset, RDF.type),None)

def get_dataset_format(data_graph: Graph, dataset:URIRef):
    return next(data_graph.objects(dataset, dmop.fileFormat,unique=True),None)