import numpy as np


def v_diag(v_matrix):
    arr = v_matrix.flatten()
    return np.diag(arr)
