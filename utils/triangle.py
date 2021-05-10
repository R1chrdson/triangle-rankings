import numpy as np


def rankify_improved(A):
    R = [0 for i in range(len(A))]
    T = [(A[i], i) for i in range(len(A))]
    T.sort(key=lambda x: x[0])
    (rank, n, i) = (1, 1, 0)

    while i < len(A):
        j = i

        while j < len(A) - 1 and T[j][0] == T[j + 1][0]:
            j += 1
        n = j - i + 1

        for j in range(n):
            idx = T[i + j][1]
            R[idx] = rank + (n - 1) * 0.5

        rank += n
        i += n
    return R


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
    r1_ranks = np.array(rankify_improved(r1_normed)) - 1
    r2_ranks = np.array(rankify_improved(r2_normed)) - 1
    diff_ranks = np.absolute(r1_ranks - r2_ranks)
    return diff, r1_ranks, r2_ranks, diff_ranks
