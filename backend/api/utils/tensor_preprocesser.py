'''
Data preprocessing functions for model training
'''

import io
import numpy as np
import pandas as pd

# TODO note: I had to change the line below to the line after it
#from keras.utils import pad_sequences
from tensorflow.keras.preprocessing.sequence import pad_sequences
# from keras.src import backend
# from keras.src.api_export import keras_export

#from keras.utils import to_categorical

from .dataLoaders import get_loader, ZipLoader
from pathlib import Path


def get_data(path:Path, label_folder):
    if not path.is_dir():
        x = get_loader(path).getDataFrame().to_numpy()
        return [x], [label_folder]
    else:
        X = []
        Y = []
        for item in path.iterdir():
            x, y = get_data(item, label_folder)
            X.extend(x)
            Y.extend(y)
        return X,Y



def read_data(data_path):

    # Initialize lists to store data
    X = list()
    Y = list()
    # Loop de folders
    for folder in Path(data_path).iterdir():

        print("Folder", folder)

        y = folder.name
        print("Label:",y)

        X_folder, Y_folder = get_data(folder,y)
        X.extend(X_folder)
        Y.extend(Y_folder)

    return X, Y

def add_padding(X):
    ''' Function to add paddind to the time series, i.e. zeros or nan values to incomplete series

    Parameters (input):
        X (list): data read from the files
        indicator_list (list): list of indicators to be considered as features

    Returns:
        X_pad: data (tensor) after adding padding
    '''
    print(X[0].shape)
    n_features = X[0].shape[1]
    X_pad = pad_sequences(X, padding="post", dtype="float64", value=np.full((n_features,), 0))

    return X_pad

def get_npz(path) -> io.BytesIO:

    zip = ZipLoader(path)

    X,Y = read_data(zip.extraction_path)
    X_pad = add_padding(X)

    buf = io.BytesIO()
    np.savez(buf, X=X_pad, Y=Y)
    buf.seek(0)

    return buf
