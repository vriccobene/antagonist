import numpy as np


def find_consecutive_true_np(arr):
    """
    Finds the consecutive true values in each column of the input numpy array `arr`.

    Args:
        arr (numpy.ndarray): A 2D numpy array.

    Returns:
        list[list[tuple[int, int]]]: A list of lists, where each inner list contains tuples representing the start and end indices of consecutive true values in the corresponding column of the input array.
    """
    result = []
    for i in range(arr.shape[1]):
        s = arr[:, i]
        m = np.r_[False, s, False]
        idx = np.flatnonzero(m[1:] != m[:-1])
        result.append(list(zip(idx[::2], idx[1::2])))
    return result
