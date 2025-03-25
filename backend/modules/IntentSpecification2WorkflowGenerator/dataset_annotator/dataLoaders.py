from abc import abstractmethod
import csv
from pathlib import Path
from typing import Dict
import pandas as pd


class DataLoader:

    fileFormat = "data file"

    def __init__(self,file):
        self.file_path = Path(file).resolve().as_posix()
        self.metadata = {
            "fileFormat": self.fileFormat,
            "path": self.file_path
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
    

class FolderLoader(DataLoader):
    fileFormat = "Folder"

    def __init__(self,dir):
        super().__init__(dir)
        self.data_loaders: list[DataLoader] = [get_loader(file.as_posix()) for file in Path(dir).iterdir()]

    def getDataFrame(self):
        dfs: list[pd.DataFrame] = []
        for dl in self.data_loaders:
            dfs.append(dl.getDataFrame())
        
        return pd.concat(dfs)
    
    def getFileMetadata(self):

        child_metadata = {}
        for i,dl in enumerate(self.data_loaders):
            dl_metadata = dl.getFileMetadata()
            for key, value in dl_metadata.items():
                child_metadata[f'file_{i}_{key}'] = value
        
        metadata = {
            ** self.metadata,
            "numFiles": str(len(self.data_loaders)),
            ** child_metadata,
        }

        return metadata
            



###################################################################
    
loaders = {
    "csv": CSVLoader,
    "parquet": ParquetLoader,
}


def get_extension(file_path) -> str:
    extension = Path(file_path).suffix
    return extension[1:]

def get_loader(path:Path) -> DataLoader:

    if Path(path).is_dir():
        return FolderLoader(path)
    
    extension = get_extension(path)
    return loaders[extension](path)