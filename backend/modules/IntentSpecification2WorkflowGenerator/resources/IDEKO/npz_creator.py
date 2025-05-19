import numpy as np
from preprocessing_functions import read_data, add_padding

indicator_list = ["f1","f2","f3"]
path= "./training_sample"
X,Y = read_data(path, indicator_list)
X_pad = add_padding(X, indicator_list)

np.savez("IDEKO", X=X_pad, Y=Y)