import csv
import os
import sys
from os import path

import pandas as pd
import scipy.stats as stats
import numpy as np

sys.path.append(os.path.abspath('..'))

from common import *


def add_dataset_info(dataset_path, graph, label):
    dataset_node = ab.term(path.basename(dataset_path))
    graph.add((dataset_node, RDF.type, dmop.TabularDataset))
    dataset = pd.read_csv(dataset_path, encoding='utf-8', delimiter=",")
    add_csv_info(dataset_path, dataset, dataset_node, graph)
    add_column_info(dataset_path, dataset, dataset_node, graph, label)


def add_csv_info(dataset_path, dataset, dataset_node, graph):
    print('\tAdding CSV info ... ', end='')
    csvfile = open(dataset_path, 'r')
    encoding = csvfile.encoding
    lines = [csvfile.readline() for _ in range(50)]
    csvfile.close()
    dialect = csv.Sniffer().sniff(''.join(lines))
    headers = csv.Sniffer().has_header(''.join(lines))

    num_rows = len(dataset.index)
    num_cols = len(dataset.columns)

    graph.add((dataset_node, dmop.fileFormat, Literal('csv')))
    graph.add((dataset_node, dmop.delimiter, Literal(dialect.delimiter)))
    graph.add((dataset_node, dmop.doubleQuote, Literal(dialect.doublequote)))
    graph.add((dataset_node, dmop.encoding, Literal(encoding)))
    graph.add((dataset_node, dmop.hasHeader, Literal(headers)))
    graph.add((dataset_node, dmop.lineDelimiter, Literal(dialect.lineterminator)))
    graph.add((dataset_node, dmop.numberOfRows, Literal(num_rows)))
    graph.add((dataset_node, dmop.numberOfColumns, Literal(num_cols)))
    graph.add((dataset_node, dmop.path, Literal(path.abspath(dataset_path))))
    graph.add((dataset_node, dmop.quoteChar, Literal(dialect.quotechar)))
    graph.add((dataset_node, dmop.skipInitialSpace, Literal(dialect.skipinitialspace)))

    print('Done!')


def get_column_type(column_type, column):
    if column_type == 'int64':
        return dmop.Integer
    elif column_type == 'float64':
        return dmop.Float
    elif column_type == 'object':
        if column.str.isnumeric().all():
            return dmop.Integer
        else:
            return dmop.String
    else:
        return dmop.String


def has_nulls(column):
    return bool(column.isnull().values.any() or column.isna().values.any())


def is_categorical(column_type, column):
    if get_column_type(column_type, column) in [dmop.Integer, dmop.Float]:
        return False
    else:
        return True


def is_unique(column_type, column):
    if column_type != 'object' and column_type != 'int64':
        return False
    else:
        return column.nunique() == column.size
    

def is_normal(column_type, column):
    if column_type in [dmop.Float]:
        clean_col = column.dropna()
        _, p_value = stats.shapiro(x=clean_col)
        if p_value < 0.05:
            sk = stats.skew(clean_col)
            ku = stats.kurtosis(clean_col)
            if abs(sk)<1 and abs(ku)<2:
                return True
            else:
                return False
        else:
            return True
        

def check_outliers(column_type, column):
    if column_type in [dmop.Float]:
        clean_col = column.dropna()

        median = np.median(clean_col)
        mad = stats.median_abs_deviation(clean_col)
        mad_constant = 1.4826 
        modified_z_scores = np.abs((clean_col - median) / (mad_constant * mad))
        
        outliers = modified_z_scores > 3.0
        outlier_indices = clean_col[outliers]

        if len(outlier_indices) > 0.25*len(clean_col):
            return False
        else:
            return True
        

def get_percentage_of_missing_rows(dataset):
    return round(dataset.isna().any(axis=1).sum()/dataset.shape[0], 3)


def add_column_info(dataset_path, dataset, dataset_node, graph, label):
    print('\tAdding column info:')
    missing_percentage = get_percentage_of_missing_rows(dataset)
    if missing_percentage != 0.0:
        graph.add((dataset_node, dmop.missingvaluesPercentage, Literal(missing_percentage)))
    graph.add((dataset_node, dmop.containsOutliers, Literal(False)))
    for col in dataset.columns:
        col_type = dataset[col].dtype.name
        col_node = ab.term(f'{path.basename(dataset_path)}/{col}')
        graph.add((dataset_node, dmop.hasColumn, col_node))
        graph.add((col_node, RDF.type, dmop.Column))
        graph.add((col_node, dmop.hasColumnName, Literal(col)))

        column_type = get_column_type(col_type, dataset[col])
        categorical = is_categorical(col_type, dataset[col])
        unique = is_unique(col_type, dataset[col])
        nulls = has_nulls(dataset[col])
        position = dataset.columns.get_loc(col)
        normality = is_normal(column_type, dataset[col])
        outliers = check_outliers(column_type, dataset[col])

        graph.add((col_node, dmop.hasDataPrimitiveTypeColumn, column_type))
        graph.add((col_node, dmop.isCategorical, Literal(categorical)))
        graph.add((col_node, dmop.isUnique, Literal(unique)))
        graph.add((col_node, dmop.containsNulls, Literal(nulls)))
        if normality:
            graph.add((col_node, dmop.isNormalDistribution, Literal(normality)))
            graph.add((dataset_node, dmop.isNormallyDistributed, Literal(normality)))
        if outliers:
            graph.add((col_node, dmop.hasOutliers, Literal(True)))
            graph.remove((dataset_node, dmop.containsOutliers, Literal(False)))
            graph.add((dataset_node, dmop.containsOutliers, Literal(True)))
        else:
            graph.add((col_node, dmop.hasOutliers, Literal(False)))
        if label != "" and col == label:  # Detect label attribute (if indicated) and annotate it
            graph.add((col_node, dmop.isFeature, Literal(False)))
            graph.add((col_node, dmop.isLabel, Literal(True)))
        else:
            graph.add((col_node, dmop.isFeature, Literal(True)))
            graph.add((col_node, dmop.isLabel, Literal(False)))
        graph.add((col_node, dmop.hasPosition, Literal(position)))
        print(f'\t\t{col}: {column_type} - {categorical=} - {unique=} - {position=} - {nulls=} - {normality=} - {outliers=}')


def read_graph(urls):
    ontology = Graph()
    for url in urls:
        ontology.parse(url)
    return ontology


def annotate_dataset(source_path, output_path, label=""):
    print(f'Annotating {source_path}')

    dataset_graph = get_graph_xp()

    add_dataset_info(source_path, dataset_graph, label)
    dataset_graph.serialize(destination=output_path)


def main():
    for file in os.listdir('./datasets'):
        if file.endswith('.csv'):
            annotate_dataset(f'./datasets/{file}', f'./annotated_datasets/{file[:-4]}_annotated.ttl')


if __name__ == '__main__':
    main()
