from pathlib import Path
import scipy.stats as stats
import numpy as np
from urllib.parse import quote

from .namespaces import *

def add_tensor_info(np_data, dataset_node, graph: Graph):
    graph.add((dataset_node, RDF.type, dmop.TensorDataset))

    X = np_data['X']
    Y = np_data['Y']

    shape_x = X.shape
    shape_y = Y.shape

    for file in np_data.files:
        shape = np_data[file].shape
        array_node = ab.term(file)
        graph.add((dataset_node, dmop.hasArray, array_node))
        graph.add((array_node, dmop.numDimensions, Literal(len(shape))))

        for i,dim in enumerate(shape):
            dim_node = ab.term(f"{file}_dimension_{i}")
            graph.add((array_node, dmop.hasFeatureDimension, dim_node))
            graph.add((dim_node, dmop.dimensionSize, Literal(dim)))