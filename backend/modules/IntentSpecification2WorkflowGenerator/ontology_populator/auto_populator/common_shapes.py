from rdflib import RDF, Literal
import sys, os

root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

from base_shape import BaseShape
from common import dmop

BASE_SHAPES = [
    BaseShape("noMissingValuesPropertyShape", 'columnar', dependences=[], transformations=[(dmop.containsNulls, Literal(False))]),
    BaseShape("isGaussianDistributed", 'columnar', dependences=[], transformations=[( dmop.isGaussian, Literal(True))]),
    BaseShape("isNumericDatatypePropertyShape", 'columnar', dependences=[], transformations=[( dmop.hasDataPrimitiveTypeColumn, dmop.Numeric)]),
    BaseShape("isIntegerDatatypePropertyShape", 'columnar', dependences=[], transformations=[( dmop.hasDataPrimitiveTypeColumn, dmop.Integer)]),
    BaseShape("isBinaryDatatypePropertyShape", 'columnar', dependences=[], transformations=[( dmop.hasDataPrimitiveTypeColumn, dmop.Binary)]),
    BaseShape("isStringDatatypePropertyShape", 'columnar', dependences=[], transformations=[( dmop.hasDataPrimitiveTypeColumn, dmop.String)]),
    BaseShape("isCategoricalOrNumericPropertyShape", 'columnar', dependences=[], transformations=[( dmop.hasDataPrimitiveTypeColumn, dmop.CategoricalOrNumeric)]),
    BaseShape("isCategoricalPropertyShape", 'columnar', dependences=[], 
              transformations=[( dmop.hasDataPrimitiveTypeColumn, dmop.Categorical), (dmop.isCategorical, Literal(True))]),
    BaseShape("minTwoClustersPropertyShape", 'columnar', dependences=[], transformations=[( dmop.numberOfDistinctValues, Literal(2)),
                                                                                    (dmop.isCategorical, Literal(True)),
                                                                                    (dmop.hasDataPrimitiveTypeColumn, dmop.Categorical)]),
    BaseShape("minZeroPropertyShape", 'columnar', dependences=[], transformations=[( dmop.minValue, Literal(0))]), 
    BaseShape("maxOnePropertyShape", 'columnar', dependences=[], transformations=[( dmop.maxValue, Literal(1))]),
    BaseShape("isScaledPropertyShape", 'columnar', dependences=[], transformations=[( dmop.isScaled, Literal(True))]),
    BaseShape("StandardizedPropertyShape", 'columnar', dependences=[], transformations=[( dmop.isStandardized, Literal(True))]),
    BaseShape("minOneComponentPropertyShape", 'dataset', dependences=[dmop.hasColumns], transformations=[( dmop.numberOfColumns, 1),( dmop.numberOfColumns, 10000)]),
    BaseShape("exactlyOneColumnPropertyShape", 'dataset', dependences=[dmop.hasColumns], transformations=[( dmop.numberOfColumns, 1)]),
    BaseShape("isTabularDatasetShape", 'dataset', dependences=[], transformations=[( RDF.type, dmop.TabularDataset)]),
    BaseShape("isDictShape", 'dataset', dependences=[dmop.hasColumns], transformations=[( RDF.type, dmop.Dict)]),
    BaseShape("isArrayShape", 'dataset', dependences=[], transformations=[( RDF.type, dmop.TabularDataset)]),
    BaseShape("isTextDocumentShape", 'dataset',dependences=[dmop.hasColumns], transformations=[( RDF.type, dmop.TextDocument)]),
    BaseShape("hasReducedDimensionality", 'dataset',dependences=[dmop.numberOfColumns], transformations=[]),
    BaseShape("hasIncreasedDimensionality", 'dataset',dependences=[dmop.numberOfColumns], transformations=[]),
    BaseShape("isContinuousPropertyShape", 'columnar', dependences=[], transformations=[(dmop.hasDataPrimitiveTypeColumn, dmop.Float)]) 

]

