from rdflib import Graph, URIRef
from ..graph_queries import data_queries
from .graph_operations import copy_subgraph


class Dataset:
    def __init__(self, data_graph: Graph, dataset:URIRef):
        self.data_graph = data_graph
        self.dataset = dataset
        self._label = None
        self._numeric_columns = None
        self._categorical_columns = None
        self._target = None
        self._format = None
        self._path = None
        self._feat_types = None
        self._graph_lite = None
    
    @property
    def label(self):
        if self._label is None:
            self._label = data_queries.get_datset_label_name(self.data_graph, self.dataset)
        return self._label
    
    @property
    def numeric_columns(self):
        if self._numeric_columns is None:
            self._numerc_columns = data_queries.get_dataset_numeric_columns(self.data_graph, self.dataset)
        return self._numerc_columns
    
    @property
    def categorical_columns(self):
        if self._categorical_columns is None:
            self._categorical_columns = data_queries.get_dataset_categorical_columns(self.data_graph, self.dataset)
        return self._categorical_columns
    
    @property
    def target(self):
        if self._target is None:
            self._target = data_queries.get_dataset_target_column(self.data_graph, self.dataset)
        return self._target
    
    @property
    def format(self):
        if self._format is None:
            self._format = data_queries.get_dataset_format(self.data_graph, self.dataset)
        return self._format
    
    @property
    def path(self):
        if self._path is None:
            self._path = data_queries.get_dataset_path(self.data_graph, self.dataset)
        return self._path
    
    @property
    def feature_types(self):
        if self._feat_types is None:
            self._feat_types = data_queries.get_dataset_feature_types(self.data_graph, self.dataset)
        return self._feat_types
    
    @property
    def data_node_graph(self):
        if self._graph_lite is None:
            self._graph_lite = Graph()
            
            # Copy all bindings
            for prefix, namespace in self.data_graph.namespaces():
                self._graph_lite.bind(prefix, namespace)

            copy_subgraph(self.data_graph, self.dataset, self._graph_lite, self.dataset)
        return self._graph_lite
    
    def clear_node_graph(self):
        self._graph_lite = None