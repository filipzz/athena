import numpy as np

def __init__(self):
    pass

def bravo_kmin(NN, wd, alpha, n):
    kmin = np.ceil((np.log(alpha) + n * (np.log(2) + np.log(NN-wd) - np.log(NN)))/(np.log(NN-wd)-np.log(wd)))
    return np.int64(kmin)


def bravo_like_kmin(NN, wd, alpha, n):
    kmin = 1
    t = stop_t(kmin, n, wd, NN, alpha, 1)
    while t == 0:
        kmin = kmin + 1
        t = stop_t(kmin, n, wd, NN, alpha, 1)

    return np.int64(kmin)

def stop_t(k, n, wd, NN, alpha, t):
    new_t = t * t_stat(k, n, wd, NN)
    r = 0
    if new_t > 1/alpha:
        r = 1
    else:
        r = 0

    return r

def t_stat(k, n, wd, NN):
    t = 1
    n_half = np.ceil(NN/2)
    ld = NN - wd
    ls = 0
    for i in range(k):
        t = t * (wd-i)/(n_half -i)

    for i in range(n-k):
        t = t * (ld - ls)/(NN - n_half - ls)
        ls = ls + 1

    return t
