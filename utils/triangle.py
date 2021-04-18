import numpy as np


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


def get_diff_ranks(r1_normed, r2_normed):
    diff = np.absolute(r1_normed - r2_normed)
    r1_ranks = np.argsort(r1_normed.argsort()[::-1])
    r2_ranks = np.argsort(r2_normed.argsort()[::-1])
    diff_ranks = np.absolute(r1_ranks - r2_ranks)
    return diff, r1_ranks, r2_ranks, diff_ranks
