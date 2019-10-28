import pytest

import numpy as np
#import rla
import risk

def test_calculate_bad_luck_cum_probab_table_b2():
    #test BRAVO kmin computation

    tests = {
        "bin" :
            {
            'test1': {
                'nn': 100,
                'wd': 60,
                'alpha': .1,
                'sample': 20,
                'expected': 13,
                'mathematica': 0.00091552734375
            },
            'test1a': {
                'nn': 100,
                'wd': 60,
                'alpha': .1,
                'sample': 40,
                'expected': 28,
                'mathematica': 0.013945882208645343780517578125
            },
            'test1b': {
                'nn': 100,
                'wd': 60,
                'alpha': .1,
                'sample': 50,
                'expected': 34,
                'mathematica': 0.0232391452769125095301205874420702457427978515625
            },
            'test1c': {
                'nn': 1000,
                'wd': 600,
                'alpha': .01,
                'sample': 50,
                'expected': 39,
                'mathematica': 0.000042520255899347603190108202397823333740234375
            },
            'test1d': {
                'nn': 1000,
                'wd': 600,
                'alpha': .1,
                'sample': 100,
                'expected': 61,
                'mathematica': 0.05283924761160804975033631572640021824346604162748246790413941820219179135165177285671234130859375000
            },
            'test2': {
                'nn': 1000,
                'wd': 600,
                'alpha': .1,
                'sample': 200,
                'expected': 116,
                'mathematica': 0.07814150217194978722862328961052978162127740034433962748552760307897734534395234640266644556552604163
            },
            'test3': {
                'nn': 1000,
                'wd': 600,
                'alpha': .01,
                'sample': 200,
                'expected': 122,
                'mathematica': 0.004825761618860028331224625528799174401859920760573927610155485947286587895900543707550333332707298253
            },
            'test4': {
                'nn': 10000,
                'wd': 5900,
                'alpha': .05,
                'sample': 100,
                'expected': 63,
                'mathematica': 0.0138487847022175811201355096247569932927569856269045729148248202733384459861554205417633056640625
            },
            },
#         "hg" : {
        #             'test1': {
        #                 'nn': 100,
        #                 'wd': 60,
        #                 'alpha': .1,
        #                 'sample': 20,
        #                 'expected': 16
        #             },
        #             'test2': {
        #                 'nn': 1000,
        #                 'wd': 600,
        #                 'alpha': .1,
        #                 'sample': 200,
        #                 'expected': 115
        #             },
        #             'test3': {
        #                 'nn': 1000,
        #                 'wd': 600,
        #                 'alpha': .01,
        #                 'sample': 200,
        #                 'expected': 120
        #             },
        #             'test4': {
        #                 'nn': 10000,
        #                 'wd': 5900,
        #                 'alpha': .05,
        #                 'sample': 100,
        #                 'expected': 63
        #             },
        #         }
   }


    errorLevel = 0.0000000001

    for type_of_test in tests.keys():
        print("test type: " + type_of_test)
        for test in tests[type_of_test]:
            expected = tests[type_of_test][test]['expected']
            nn = tests[type_of_test][test]['nn']
            wd = tests[type_of_test][test]['wd']
            alpha = tests[type_of_test][test]['alpha']
            n = tests[type_of_test][test]['sample']
            print("\n" + test + "\t" + str(nn) + "\t" + str(wd) + "\t" + str(n))

            computedFrac = risk.calculate_bad_luck_cum_probab_table_b2_frac(n, wd, nn, alpha, "risk", type_of_test)
            computedNumpy = risk.calculate_bad_luck_cum_probab_table_b2_longdouble(n, wd, nn, alpha, "risk", type_of_test)
            computedFloat = risk.calculate_bad_luck_cum_probab_table_b2(n, wd, nn, alpha, "risk", type_of_test)
            computedSympy = risk.calculate_bad_luck_cum_probab_table_b2_sympy(n, wd, nn, alpha, "risk", type_of_test)

            expected = tests[type_of_test][test]["mathematica"]
            print("math:  " + "{:,.80f}".format(expected))



            #assert np.abs(computedFrac["sum"] -  computedNumpy["sum"]) < 0.00000000000000000001, 's_w failed: got {}, expected {}'.format(computedFrac["sum"], computedNumpy["sum"])
            assert np.abs(computedFrac["sum"] - expected) < errorLevel, 's_w failed: got {}, expected {}'.format(computedFrac["sum"], computedFloat["sum"])
            assert np.abs(computedNumpy["sum"] - expected) < errorLevel, 's_w failed: got {}, expected {}'.format(computedNumpy["sum"], computedFloat["sum"])
            assert np.abs(computedSympy["sum"] - expected) < errorLevel, 's_w failed: got {}, expected {}'.format(computedNumpy["sum"], computedSympy["sum"])
            assert np.abs(computedFloat["sum"] - expected) < errorLevel, 's_w failed: got {}, expected {}'.format(computedNumpy["sum"], computedSympy["sum"])

