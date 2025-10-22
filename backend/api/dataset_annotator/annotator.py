
from pathlib import Path
from typing import Tuple
from urllib.parse import quote
#sys.path.append(str(Path('..').resolve()))

from utils import dataLoaders
from .namespaces import *
from .tabular_annotator import add_dataframe_info
from .tensor_annotator import add_tensor_info

def add_dataset_info(dataset_path, graph, label):
    dataset_node = ab.term(quote(Path(dataset_path).with_suffix('').name))
    data_loader: dataLoaders.DataLoader = dataLoaders.get_loader(dataset_path)
    #dataset = data_loader.getDataFrame()#pd.read_csv(dataset_path, encoding='utf-8', delimiter=",")
    add_metadata_info(data_loader.getFileMetadata(), dataset_node, graph)

    if data_loader.fileFormat in ["NumpyZip"]:
        print('Adding tensor info ... ')
        add_tensor_info(data_loader.getDataFrame(), dataset_node, graph)
    else:
        print('Adding dataframe info ... ')
        add_dataframe_info(data_loader.getDataFrame(), dataset_node, graph, label)
    return dataset_node


def add_metadata_info(metadata, dataset_node, graph:Graph):
    print('\tAdding info ... ', end='')

    for key,value in metadata.items():
        graph.add((dataset_node,dmop[key],Literal(value)))
    print('Done!')

def annotate_dataset(source_path, label="") -> Tuple[URIRef,Graph]:
    print(f'Annotating {source_path}')

    dataset_graph = get_annotator_base_graph()
    dataset_node = add_dataset_info(source_path, dataset_graph, label)

    return dataset_node, dataset_graph


def main():
    for file in Path('./datasets').iterdir():
        #if file.endswith('.csv'):
        d = annotate_dataset(file)
        with open(f'./annotated_datasets/{file.name}_annotated.ttl', mode='w') as f:
            f.write(d)

    #annotate_dataset('./T1003.001_ OS Credential Dumping_ LSASS Memory2024-09-07 2024-09-13', './annotated_datasets/hierarchy.ttl')


if __name__ == '__main__':
    main()
