from abc import abstractmethod
import csv
import os
from typing import Dict
import pandas as pd


class DataLoader:

    fileFormat = "data file"

    def __init__(self,file):
        self.file_path = file
        self.metadata = {
            "fileFormat": self.fileFormat,
            "path": os.path.abspath(self.file_path)
        }

    @abstractmethod
    def getDataFrame(self) -> pd.DataFrame:
        pass

    def getFileMetadata(self) -> Dict:
        return self.metadata
    
    
class CSVLoader(DataLoader):
    fileFormat = "CSV"

    def getDataFrame(self) -> pd.DataFrame:
        return pd.read_csv(self.file_path,encoding='utf-8')
    
    def getFileMetadata(self):

        with open(self.file_path, 'r') as csvfile:
            encoding = csvfile.encoding
            lines = [csvfile.readline() for _ in range(50)]

        dialect = csv.Sniffer().sniff(''.join(lines))
        header = csv.Sniffer().has_header(''.join(lines))

        metadata = {
            **self.metadata,
            "delimiter": dialect.delimiter,
            "doubleQuote": dialect.doublequote,
            "lineDelimiter": dialect.lineterminator,
            "quoteChar": dialect.quotechar,
            "skipInitialSpace": dialect.skipinitialspace,
            "encoding": encoding,
            "hasHeader": header,
        }

        return metadata
    
class ParquetLoader(DataLoader):
    fileFormat = "Parquet"

    def getDataFrame(self):
        return pd.read_parquet(self.file_path)
    


###################################################################
    
loaders = {
    "csv": CSVLoader,
    "parquet": ParquetLoader,
}


def get_extension(file_path) -> str:
    _, extension = os.path.splitext(file_path)
    return extension[1:]

def get_loader(path) -> DataLoader:
    extension = get_extension(path)
    return loaders[extension](path)