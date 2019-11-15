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


    error_level = 0.0000000001

    for type_of_test in tests.keys():
        print("test type: " + type_of_test)
        for test in tests[type_of_test]:
            expected = tests[type_of_test][test]['expected']
            nn = tests[type_of_test][test]['nn']
            wd = tests[type_of_test][test]['wd']
            alpha = tests[type_of_test][test]['alpha']
            n = tests[type_of_test][test]['sample']
            print("\n" + test + "\t" + str(nn) + "\t" + str(wd) + "\t" + str(n))

            #computedFrac = risk.calculate_bad_luck_cum_probab_table_b2_frac(n, wd, nn, alpha, "risk", type_of_test)
            #computedNumpy = risk.calculate_bad_luck_cum_probab_table_b2_longdouble(n, wd, nn, alpha, "risk", type_of_test)
            computedFloat = risk.calculate_bad_luck_cum_probab_table_b2(n, wd, nn, alpha, "risk", type_of_test)
            #computedSympy = risk.calculate_bad_luck_cum_probab_table_b2_sympy(n, wd, nn, alpha, "risk", type_of_test)

            expected = tests[type_of_test][test]["mathematica"]
            print("math:  " + "{:,.80f}".format(expected))



            #assert np.abs(computedFrac["sum"] -  computedNumpy["sum"]) < 0.00000000000000000001, 's_w failed: got {}, expected {}'.format(computedFrac["sum"], computedNumpy["sum"])
            #assert np.abs(computedFrac["sum"] - expected) < error_level, 's_w failed: got {}, expected {}'.format(computedFrac["sum"], computedFloat["sum"])
            #assert np.abs(computedNumpy["sum"] - expected) < error_level, 's_w failed: got {}, expected {}'.format(computedNumpy["sum"], computedFloat["sum"])
            #assert np.abs(computedSympy["sum"] - expected) < error_level, 's_w failed: got {}, expected {}'.format(computedNumpy["sum"], computedSympy["sum"])
            assert np.abs(computedFloat["sum"] - expected) < error_level, 's_w failed: got {}, expected {}'.format(computedNumpy["sum"], computedSympy["sum"])


def test_find_risk_bravo_bbb():
    error_level = 0.0001

    tests = { "bin" :
                {
                'test1': {
                    'nn': 1000,
                    'wd': 600,
                    'alpha': .1,
                    'round_schedule': [19, 50, 120, 350],
                    'expected': {
                        'kmins': [17, 34, 72, 199],
                        'risk_goal': [15/16384, 13082475751189/562949953421312, 40749282220389162961500860981726755/
664613997892457936451903530140172288,101293204100778781835614887083515247417594116825324977213381556544607443001150820502801193446230790501247/1146749307995035755805410447651043470398282494584140561868794419693461438044242404035009276555062843277312],
                        'prob_stop': [38434344561/3814697265625, 4445872486532286446994218066869317/17763568394002504646778106689453125, 500942470229451850783617943781885554916226035827938067635424137086658784557215124513/752316384526264005099991383822237233803945956334136013765601092018187046051025390625, 8360478374091637420299011707945839598880299643212796316798832891578583488138622683448763328560029809670372869836608660428148617406501785794336020100205862372794065868463331835066004720695449808776853866760315539473018337174228189986957936964949/8720301752336692674375790010874488521209030111868275918694502588101445281270890775111755537873626935189690050913803315980686503313323354729660356852798776565288650645264322364871641843436828812909146772976154426970651911688037216663360595703125]
                    }
                },
                'mercer20': {
                    'nn': 20312,
                    'wd': 15038,
                    'alpha': .1,
                    'round_schedule': [20],
                    'expected': {
                        'kmins': [15],
                        'risk_goal': [29951/524288],
                        'prob_stop': [45387000688971984253283143506722021811496015202994035020291729150044359623960373/68143407777721406689115487311226665209092096501139833817629064443449642464575488]
                    }
                },
                'mercer21': {
                    'nn': 20312,
                    'wd': 15038,
                    'alpha': .1,
                    'round_schedule': [21],
                    'expected': {
                        'kmins': [16],
                        'risk_goal': [29951/524288],
                        'prob_stop': [45387000688971984253283143506722021811496015202994035020291729150044359623960373/68143407777721406689115487311226665209092096501139833817629064443449642464575488]
                    }
                },
                'mercer22': {
                    'nn': 20312,
                    'wd': 15038,
                    'alpha': .1,
                    'round_schedule': [22],
                    'expected': {
                        'kmins': [16],
                        'risk_goal': [264129/4194304],
                        'prob_stop': [10223342799872760455580185669671656195631489717732381132396795064194264043289770499802465/14057213096020620171869550732065799456972210912915982804539389892641645842892084463271936]
                    }
                },
                'mercer23': {
                    'nn': 20312,
                    'wd': 15038,
                    'alpha': .1,
                    'round_schedule': [23],
                    'expected': {
                        'kmins': [17],
                        'risk_goal': [264129/4194304],
                        'prob_stop': [10223342799872760455580185669671656195631489717732381132396795064194264043289770499802465/14057213096020620171869550732065799456972210912915982804539389892641645842892084463271936]
                    }
                },
                'mercer24': {
                    'nn': 20312,
                    'wd': 15038,
                    'alpha': .1,
                    'round_schedule': [24],
                    'expected': {
                        'kmins': [18],
                        'risk_goal': [264129/4194304],
                        'prob_stop': [10223342799872760455580185669671656195631489717732381132396795064194264043289770499802465/14057213096020620171869550732065799456972210912915982804539389892641645842892084463271936]
                    }
                },
                'mercer25': {
                    'nn': 20312,
                    'wd': 15038,
                    'alpha': .1,
                    'round_schedule': [25],
                    'expected': {
                        'kmins': [18],
                        'risk_goal': [1113987/16777216],
                        'prob_stop': [5655326635682294937884304355816403624524483073879214504163753660967897071500641573441247843899836283/7362703463040120536253437318118628748370083947998408834680773167801256672081478479086868948412530688]
                    }
                },
                }
    }

    for type_of_test in tests.keys():
        print("test type: " + type_of_test)
        for test in tests[type_of_test]:
            expected = tests[type_of_test][test]['expected']
            nn = tests[type_of_test][test]['nn']
            wd = tests[type_of_test][test]['wd']
            alpha = tests[type_of_test][test]['alpha']
            round_schedule = tests[type_of_test][test]['round_schedule']
            print("\n" + test + "\t" + str(nn) + "\t" + str(wd) + "\t" + str(round_schedule))
            computed = risk.find_risk_bravo_bbb(nn, wd, alpha, type_of_test, round_schedule, "false")
            print(computed)
            kmins = computed['kmins']
            risk_goal = computed['risk_goal']
            prob_stop = computed['prob_stop']

            expected_kmins = expected['kmins']
            expected_risk_goal = expected['risk_goal']
            expected_prob_stop = expected['risk_goal']

            #for i in range(len(kmins)):
             #   assert kmins[i] == expected_kmins[i], 's_w failed: got {}, expected {}'.format(kmins[i], expected_kmins[i])

            assert kmins == expected_kmins, 's_w failed: got {}, expected {}'.format(kmins, expected_kmins)

            # TODO: check values of risk_goal/prob_stop
            for rg_com, rg_exp in zip(risk_goal, expected_risk_goal):
                assert np.abs(rg_com - rg_exp) < error_level, 's_w failed: got {}, expected {}'.format(rg_com, rg_exp)
            #for i in range(len(risk_goal)):
            #    assert np.abs(risk_goal[i] - expected_risk_goal[i]) < error_level, 's_w failed: got {}, expected {}'.format(risk_goal[i], expected_risk_goal[i])




