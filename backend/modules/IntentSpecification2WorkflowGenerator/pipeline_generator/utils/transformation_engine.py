from rdflib import Graph, URIRef, Literal
from typing import List, Tuple, Dict
from common import *

from .graph_operations import copy_subgraph
from .dataset import Dataset


def run_copy_transformation(ontology: Graph, data_graph: Graph, transformation: URIRef, inputs: List[URIRef],
                            outputs: List[URIRef]):
    input_index = next(ontology.objects(transformation, tb.copy_input, True)).value
    output_index = next(ontology.objects(transformation, tb.copy_output, True)).value

    input = inputs[input_index - 1][0]
    output = outputs[output_index - 1][0]

    copy_subgraph(data_graph, input, data_graph, output)


def run_component_transformation(ontology: Graph, dataset:Dataset, component_transformations, inputs: List[Tuple[URIRef,URIRef]],
                                 outputs:  List[Tuple[URIRef,URIRef]],
                                 parameters_specs: Dict[URIRef, Tuple[URIRef, Literal, Literal]]) -> None:
    data_graph = dataset.data_node_graph

    
    for transformation in component_transformations:
        if (transformation, RDF.type, tb.CopyTransformation) in ontology:
            run_copy_transformation(ontology, data_graph, transformation, inputs, outputs)
        elif (transformation, RDF.type, tb.LoaderTransformation) in ontology:
            for o,_ in outputs:
                copy_subgraph(data_graph, dataset.dataset, data_graph, o)
        else:
            prefixes = f'''
PREFIX tb: <{tb}>
PREFIX ab: <{ab}>
PREFIX rdf: <{RDF}>
PREFIX rdfs: <{RDFS}>
PREFIX owl: <{OWL}>
PREFIX xsd: <{XSD}>
PREFIX dmop: <{dmop}>
'''
            query = next(ontology.objects(transformation, tb.transformation_query, True)).value
            query = prefixes + query
            for i in range(len(inputs)):
                query = query.replace(f'$input{i + 1}', f'{inputs[i][0].n3()}')
            for i in range(len(outputs)):
                query = query.replace(f'$output{i + 1}', f'{outputs[i][0].n3()}')
            for order, (param_spec, value) in enumerate(parameters_specs.items()):
                query = query.replace(f'$param{order + 1}', f'{value}') #TODO allow transformation engine to have access to all the parameters. Otherwise, some transformations can not be done (see numberofrows on partitioning)
                query = query.replace(f'$parameter{order + 1}', f'{value}')
            data_graph.update(query)