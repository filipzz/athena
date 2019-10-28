import os
import sys
import pytest



import rla

def test_bravo_kmin():
    #test BRAVO kmin computation

    tests = {
        'test1': {
            'nn': 100,
            'wd': 60,
            'alpha': .1,
            'sample': 20,
            'expected': 17
        },
        'test2': {
            'nn': 1000,
            'wd': 600,
            'alpha': .1,
            'sample': 200,
            'expected': 116
        },
        'test3': {
            'nn': 1000,
            'wd': 600,
            'alpha': .01,
            'sample': 200,
            'expected': 122
        },
        'test4': {
            'nn': 10000,
            'wd': 5900,
            'alpha': .05,
            'sample': 100,
            'expected': 63
        },


    }

    for test in tests:
        expected = tests[test]['expected']
        nn = tests[test]['nn']
        wd = tests[test]['wd']
        alpha = tests[test]['alpha']
        n = tests[test]['sample']

        computed = rla.bravo_kmin(nn, wd, alpha, n)

        assert expected == computed, 's_w failed: got {}, expected {}'.format(computed, expected)


def test_bravo_like_kmin():
    #test BRAVO_like_kmin computation

    tests = {
        'test1': {
            'nn': 100,
            'wd': 60,
            'alpha': .1,
            'sample': 20,
            'expected': 16
        },
        'test2': {
            'nn': 1000,
            'wd': 600,
            'alpha': .1,
            'sample': 200,
            'expected': 115
        },
        'test3': {
            'nn': 1000,
            'wd': 600,
            'alpha': .01,
            'sample': 200,
            'expected': 120
        },
        'test4': {
            'nn': 10000,
            'wd': 5900,
            'alpha': .05,
            'sample': 100,
            'expected': 63
        },


    }

    for test in tests:
        expected = tests[test]['expected']
        nn = tests[test]['nn']
        wd = tests[test]['wd']
        alpha = tests[test]['alpha']
        n = tests[test]['sample']

        computed = rla.bravo_like_kmin(nn, wd, alpha, n)

        assert expected == computed, 's_w failed: got {}, expected {}'.format(computed, expected)
