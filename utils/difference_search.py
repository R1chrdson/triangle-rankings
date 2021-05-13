import pandas as pd
import numpy as np
from utils.helpers import get_normed


def get_percent(x, m):
    if m == 0:
        return 0
    return x / m


def advantages_matrix_positive(x, max_th, min_th):
    if x > max_th:
        return 7
    if x < min_th:
        return 1
    return 3


def advantages_matrix_element(x, p7, q1):
    if x == 0:
        return 1

    max_th = 1 - p7

    if x > 0:
        return advantages_matrix_positive(x, max_th, q1)
    return 1 / advantages_matrix_positive(abs(x), max_th, q1)


def geo_mean(iterable):
    a = np.log(iterable)
    return np.exp(a.mean())


def difference_search_processing(r, p7, q1):
    r_diff_matrix = r.apply(lambda x: x - r)
    dr = r_diff_matrix.max().max()
    r_diff_percents = r_diff_matrix.applymap(lambda x: get_percent(x, dr))
    r_advantages_matrix = r_diff_percents.applymap(lambda x: advantages_matrix_element(x, p7, q1))
    r_geo_mean = r_advantages_matrix.apply(geo_mean, axis=1)
    r_geo_mean_normed = get_normed(r_geo_mean)
    return r_diff_matrix, r_diff_percents, r_advantages_matrix, r_geo_mean, r_geo_mean_normed


def difference_search(r1_n, r2_n, p7, q1):
    r1_n = pd.Series(r1_n)
    r2_n = pd.Series(r2_n)
    return difference_search_processing(r1_n, p7, q1), difference_search_processing(r2_n, p7, q1)
