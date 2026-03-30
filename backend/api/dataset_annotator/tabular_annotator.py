
from pathlib import Path
import scipy.stats as stats
import numpy as np
from urllib.parse import quote
#sys.path.append(str(Path('..').resolve()))
import pandas as pd

from .namespaces import *



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
    elif column.nunique() < 20 and column.nunique()/len(column) < 0.5: 
        #columns should be categorical if values are repeated accross the column. Otherwise it's text.
        #Categorical variable with more than 20 levels is rare
        return True
    return False

def get_distinct_values(column):
    return column.nunique()
    

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

def isScaled(column:pd.Series):
    column.mean()

def check_scaled(series: pd.Series, tol=1e-5):
    """
    Check if a pandas Series is scaled.
    """

    series_clean = pd.to_numeric(series, errors='coerce').dropna()
    
    if series_clean.empty:
        return False
    
    
    # Check Min-Max scaling (0-1)
    min_val, max_val = series_clean.min(), series_clean.max()
    min_max_scaled = np.isclose(min_val, 0, atol=tol) and np.isclose(max_val, 1, atol=tol)
    
    # Check Standardization (mean 0, std 1)
    mean_val, std_val = series_clean.mean(), series_clean.std(ddof=0)
    standardized = np.isclose(mean_val, 0, atol=tol) and np.isclose(std_val, 1, atol=tol)
    
    return bool(min_max_scaled) or bool(standardized)

        

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
    if dataset.shape[0] == 0:
        return 0
    return round(dataset.isna().any(axis=1).sum()/dataset.shape[0], 3)

def get_min_value(column, isInteger):
    numeric_only:pd.Series = pd.to_numeric(column, errors='coerce')
    min_value = Literal(numeric_only.min(), datatype=XSD.integer if isInteger else XSD.decimal) if numeric_only.notna().any() else dmop.Undefined
    return min_value

def get_max_value(column, isInteger):
    numeric_only:pd.Series = pd.to_numeric(column, errors='coerce')
    min_value = Literal(numeric_only.max(), datatype=XSD.integer if isInteger else XSD.decimal) if numeric_only.notna().any() else dmop.Undefined
    return min_value

def add_dataframe_info(dataset, dataset_node, graph: Graph, label):
    graph.add((dataset_node, RDF.type, dmop.TabularDataset))

    print('\tAdding dimension info:')
    num_rows = len(dataset.index)
    num_cols = len(dataset.columns)
    graph.add((dataset_node, dmop.numberOfRows, Literal(num_rows)))
    graph.add((dataset_node, dmop.numberOfColumns, Literal(num_cols)))

    print('\tAdding column info:')
    # missing_percentage = get_percentage_of_missing_rows(dataset)
    # if missing_percentage != 0.0:
    #     graph.add((dataset_node, dmop.missingvaluesPercentage, Literal(missing_percentage)))
    # graph.add((dataset_node, dmop.containsOutliers, Literal(False)))

    dataset_path = next(graph.objects(dataset_node,dmop.path,unique=True),"...")
    dataset_name = quote(Path(dataset_path).with_suffix('').name)
 
    for col in dataset.columns:
        col_type = dataset[col].dtype.name
        col_node = ab.term(f'{col}')
        graph.add((dataset_node, dmop.hasColumn, col_node))
        graph.add((col_node, RDF.type, dmop.Column))
        graph.add((col_node, dmop.hasColumnName, Literal(col)))

        column_type = get_column_type(col_type, dataset[col])
        categorical = is_categorical(col_type, dataset[col])
        if categorical:
            column_type = dmop.Categorical
        distinct_values = get_distinct_values(dataset[col])
        nulls = has_nulls(dataset[col])
        position = dataset.columns.get_loc(col)
        normality = is_normal(column_type, dataset[col])
        outliers = check_outliers(column_type, dataset[col])
        min_value = get_min_value(dataset[col], column_type == dmop.Integer)
        max_value = get_max_value(dataset[col], column_type == dmop.Integer)
        scaled = check_scaled(dataset[col])

        graph.add((col_node, dmop.hasDataPrimitiveTypeColumn, column_type))
        graph.add((col_node, dmop.isCategorical, Literal(categorical)))
        graph.add((col_node, dmop.numberOfDistinctValues, Literal(distinct_values)))
        graph.add((col_node, dmop.minValue, min_value))
        graph.add((col_node, dmop.maxValue, max_value))

        graph.add((col_node, dmop.isStandardized, Literal(not normality is None)))
        graph.add((col_node, dmop.isScaled, Literal(scaled)))
        graph.add((col_node, dmop.hasOutliers, Literal(not outliers is None)))

        graph.add((col_node, dmop.containsNulls, Literal(nulls)))

        if label != "" and col == label:  # Detect label attribute (if indicated) and annotate it
            graph.add((col_node, dmop.isFeature, Literal(False)))
            graph.add((col_node, dmop.isLabel, Literal(True)))
        else:
            graph.add((col_node, dmop.isFeature, Literal(True)))
            graph.add((col_node, dmop.isLabel, Literal(False)))
        graph.add((col_node, dmop.hasPosition, Literal(position)))
        print(f'\t\t{col}: {column_type} - {categorical=} - {distinct_values=} - {position=} - {nulls=} - {normality=} - {outliers=}')



