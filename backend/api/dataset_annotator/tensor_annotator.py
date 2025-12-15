from pathlib import Path
import scipy.stats as stats
import numpy as np
from urllib.parse import quote

from .namespaces import *


def get_column_type(column_type):
    if column_type == 'int64':
        return dmop.Integer
    elif column_type == 'float64':
        return dmop.Float
    elif column_type.kind in {'U', 'S'}:
        return dmop.String
    else:
        return dmop.UnknownType

def add_tensor_info(np_data, dataset_node, graph: Graph):
    graph.add((dataset_node, RDF.type, dmop.TensorDataset))

    labeledShape = False

    if len(np_data.files) == 2:
        files = np_data.files
        X = np_data[files[0]]
        Y = np_data[files[1]]

        if X.shape[0] == Y.shape[0] and (len(X.shape) == 1 or len(Y.shape) == 1):
            # A labeled dataset is only considered if exactly two arrays are passed: X (dimensions n * m * k *...) and Y (1-dimensional array with n elements)
            # X and Y can appear in any order and any name

            labeledShape = True
            numObservations = X.shape[0]
            
        

    for file in np_data.files:
        data = np_data[file]
        shape = data.shape
        array_node = ab.term(f"{dataset_node.fragment}_{file}")
        graph.add((array_node, RDF.type, dmop.Array))
        graph.add((dataset_node, dmop.hasArray, array_node))
        graph.add((array_node, dmop.numDimensions, Literal(len(shape))))

        dtype = data.dtype
        dmop_type = get_column_type(dtype)
        graph.add((array_node, dmop.hasDatatype, dmop_type))
        
        if labeledShape and len(shape) == 1:
            graph.add((array_node, dmop.isLabel, Literal(True))) #Considering a label only 1 dimensional array with n elements
        else:
            graph.add((array_node, dmop.isLabel, Literal(False)))

        for i,dim in enumerate(shape):
            dim_node = ab.term(f"{array_node.fragment}_dimension_{i}")
            graph.add((dim_node, RDF.type, dmop.Dimension))
            graph.add((array_node, dmop.hasFeatureDimension, dim_node))
            graph.add((dim_node, dmop.dimensionSize, Literal(dim)))
            

            #TODO allow any dimension to be the one used for the horizontal partition
            if labeledShape and i == 0:
                graph.add((dim_node, dmop.isHorizontalPartitionDimension, Literal(True)))
            else:
                graph.add((dim_node, dmop.isHorizontalPartitionDimension, Literal(False)))
