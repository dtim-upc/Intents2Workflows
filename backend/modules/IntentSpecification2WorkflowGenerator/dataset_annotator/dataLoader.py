from abc import abstractmethod
import csv
from os import path
from typing import Dict
import pandas as pd


class DataLoader:

    fileFormat = "data file"

    def __init__(self,file):
        self.file_path = file
        self.metadata = {
            "format": self.fileFormat,
            "path": path.abspath(self.file_path)
        }

    @abstractmethod
    def getDataFrame(self) -> pd.DataFrame:
        pass

    def getFileMetadata(self) -> Dict:
        return self.metadata
    
    
class CSVLoader(DataLoader):
    fileFormat = "CSV"

    def getDataFrame(self) -> pd.DataFrame:
        return pd.read_csv(self.file_path)
    
    def getFileMetadata(self):

        with open(self.file_path, 'r') as csvfile:
            encoding = csvfile.encoding
            lines = [csvfile.readline() for _ in range(50)]

        dialect = csv.Sniffer().sniff(''.join(lines))
        headers = csv.Sniffer().has_header(''.join(lines))

        metadata = {
            **self.metadata,
            "delimiter": dialect.delimiter,
            "doublequote": dialect.doublequote,
            "linedelimiter": dialect.lineterminator,
            "quotechar": dialect.quotechar,
            "skipinitalspace": dialect.skipinitialspace,
            "encoding": encoding,
            "hasheaders": headers,
        }

        return metadata
    
class ParquetLoader(DataLoader):
    fileFormat = "Parquet"

    def getDataFrame(self):
        return pd.read_parquet(self.file_path)