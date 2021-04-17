import numpy as np
import pandas as pd


def rnd():
    return np.random.random()


def get_left_triangle(a, m):
    return a + (m - a) * np.sqrt(rnd())


def get_right_triangle(b, m):
    return m + (b - m) * (1 - np.sqrt(rnd()))


def triangular(a, b, m, size):
    if a > b:
        raise ValueError('a > b')
    if m < a:
        raise ValueError('m < a')
    if m > b:
        raise ValueError('m > b')
    if size <= 0:
        raise ValueError('size <= 0')

    if a == b:
        return np.array([np.float64(a) for _ in range(size)])

    p1 = (m - a) / (b - a)
    return np.array([get_left_triangle(a, m) if rnd() < p1 else get_right_triangle(b, m) for _ in range(size)])


def metric(r1, r2):
    r1_normed = r1 / sum(r1) if sum(r1) else 1 / len(r1)
    r2_normed = r2 / sum(r2) if sum(r2) else 1 / len(r2)
    diff = np.absolute(r1_normed - r2_normed)
    metric = diff.sum()

    r1_ranks = np.argsort(r1.argsort()[::-1])
    r2_ranks = np.argsort(r2.argsort()[::-1])
    diff_ranks = np.absolute(r1_ranks - r2_ranks)
    metric_ranks = diff_ranks.sum()

    data = {'R1': r1, 'R2': r2, 'R1_n': r1_normed, 'R2_n': r2_normed, 'D_n': diff,
            'R1_r': r1_ranks, 'R2_r': r2_ranks, 'D_r': diff_ranks}
    df = pd.DataFrame(data=data)
    df['R1'] = df['R1'].map(lambda x: '{0:5.2f}'.format(x))
    df['R2'] = df['R2'].map(lambda x: '{0:5.2f}'.format(x))
    df['R1_n'] = df['R1_n'].map(lambda x: '{0:5.4f}'.format(x))
    df['R2_n'] = df['R2_n'].map(lambda x: '{0:5.4f}'.format(x))
    df['D_n'] = df['D_n'].map(lambda x: '{0:5.4f}'.format(x))
    metric_str = '{0:5.4f}'.format(metric)
    return df, metric_str, metric_ranks
