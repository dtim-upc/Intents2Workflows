from abc import abstractmethod
import csv
from pathlib import Path
from typing import Dict
import pandas as pd
import numpy as np
import zipfile
import tempfile
import shutil
import atexit
import laspy


# Create a temporary directory
temp_dir = tempfile.mkdtemp()

# Register a cleanup function that will delete the directory upon exit
def cleanup_temp_dir():
    if Path(temp_dir).is_dir():
        shutil.rmtree(temp_dir)
        print(f"Temporary directory {temp_dir} cleaned up.")

atexit.register(cleanup_temp_dir)

print(f"Temporary directory created: {temp_dir}")


class DataLoader:
    fileFormat = "data file"

    def __init__(self,file,displayed_path=None):
        self.file_path = Path(file).as_posix()
        self.metadata = {
            "fileFormat": self.fileFormat,
            "path": self.file_path,
            "local_path":displayed_path
        }

    @abstractmethod
    def getDataFrame(self) -> pd.DataFrame:
        pass

    def getFileMetadata(self) -> Dict:
        return self.metadata
    
    
class CSVLoader(DataLoader):
    fileFormat = "CSV"

    def __init__(self,file, local_path=None):
        super().__init__(file, local_path)

        with open(self.file_path, 'r') as csvfile:
            self.encoding = csvfile.encoding
            lines = [csvfile.readline() for _ in range(50)]
        
        self.dialect = csv.Sniffer().sniff(''.join(lines))
        self.hasHeader = csv.Sniffer().has_header(''.join(lines))


    def getDataFrame(self) -> pd.DataFrame:
        return pd.read_csv(self.file_path, encoding=self.encoding, delimiter=self.dialect.delimiter)
    
    def getFileMetadata(self):
        metadata = {
            **self.metadata,
            "delimiter": self.dialect.delimiter,
            "doubleQuote": self.dialect.doublequote,
            "lineDelimiter": self.dialect.lineterminator,
            "quoteChar": self.dialect.quotechar,
            "skipInitialSpace": self.dialect.skipinitialspace,
            "encoding": self.encoding,
            "hasHeader": self.hasHeader,
        }

        return metadata
    
class ParquetLoader(DataLoader):
    fileFormat = "Parquet"

    def getDataFrame(self):
        return pd.read_parquet(self.file_path)

class NumpyZipLoader(DataLoader):
    fileFormat = "NumpyZip"

    def getDataFrame(self):
        npz_data = np.load(self.file_path, allow_pickle=False)
        files = npz_data.files
        assert len(files) == 2
        assert npz_data[files[0]].shape[0] == npz_data[files[1]].shape[0]
        return npz_data
        
    

class FolderLoader(DataLoader):
    fileFormat = "Folder"

    def __init__(self,dir, local_dir=None):
        super().__init__(dir, local_dir)
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
            "numFiles": len(self.data_loaders),
            ** child_metadata,
        }

        return metadata
    
class ZipLoader(FolderLoader):
    fileFormat = "ZIP"

    def __init__(self,dir,local_dir=None):
        zfile = zipfile.ZipFile(dir, mode='r')
        self.extraction_path = Path(temp_dir).joinpath(Path(dir).with_suffix('').name)
        zfile.extractall(self.extraction_path)
        super().__init__(self.extraction_path, local_dir)
        self.metadata['path'] = Path(dir).resolve().as_posix()


class LidarLoader(DataLoader):
    fileFormat = "Lidar_point_cloud" 

    def getDataFrame(self):
        laspy_data = laspy.read(self.file_path)
        xyz = laspy_data.xyz
        xyz_df = pd.DataFrame(xyz, columns=["x", "y", "z"]) #get coordinates scaled
        points_df = pd.DataFrame(laspy_data.points.array)
        points_df = points_df.drop(columns=["X", "Y", "Z"]) #drop unscaled columns

        # Merge both
        full_df = pd.concat([xyz_df, points_df], axis=1)
        return full_df




class DummyLoader(DataLoader):
    fileFormat = "Unsupported"
    
    def getDataFrame(self):
        return pd.DataFrame()
    
    def getFileMetadata(self):
        metadata = {
            **self.metadata,
            "ignored": True
        }
        return metadata

            



###################################################################
    
loaders = {
    "csv": CSVLoader,
    "parquet": ParquetLoader,
    "zip": ZipLoader,
    "npz": NumpyZipLoader,
    "las": LidarLoader,
    "": FolderLoader,
}


def get_extension(file_path) -> str:
    extension = Path(file_path).suffix
    return extension[1:]

def get_loader(path:Path, local_path=None) -> DataLoader:

    if Path(path).is_dir():
        return FolderLoader(path,local_path)
    
    extension = get_extension(path)
    print(loaders.get(extension,DummyLoader))
    return loaders.get(extension,DummyLoader)(path,local_path)