import schedule
import numpy as np


def test_find_new_kmins():

    error_level = 0.0001

    tests = { "bin" :
                {
                # timing: for this parameters:
                    # mathematica: preprocessing (BRAVO): 287.7
                    # mathematica: main part (Aurror): 47.91
                    # mathematica: max memory consumption: 3 175 671 976 B
                    # python all NUMPY + SCIPY:
                        # real	1m55,189s
                        # user	1m55,076s
                        # sys	0m0,608s
                        # max memory consumption: 786 876 kB
                    # python all SYMPY:
                        # real	20m0,913s
                        # user	19m55,100s
                        # sys	0m6,120s
                      # max memory consumption: 17 486 068 kB
                    # python SYMPY just main part (with risk precomputed): 116.124:
                        # real	1m53,161s
                        # user	1m52,900s
                        # sys	0m0,704s


                'test1': {
                    'nn': 14000,
                    'wd': 7700,
                    'alpha': .1,
                    'round_schedule': [193, 332, 587],#, 974, 2155],
                    'risk_goal': [.024, .0479, .0718],#, .0862, .0948],
                    'expected': {
                        'kmins': [111, 183, 315],#, 516, 1126],
                        'risk_expended': [.0218, .0459, .0699],#, .085, .0944],
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
            risk_goal = tests[type_of_test][test]['risk_goal']
            expected_kmins = expected['kmins']
            expected_risk_expended = expected['risk_expended']

            print("\n" + test + "\t" + str(nn) + "\t" + str(wd) + "\t" + str(round_schedule))

            computed = schedule.find_new_kmins(nn, wd, alpha, round_schedule, risk_goal)
            print(computed)
            kmins = computed['kmin_new']
            risk_goal = computed['risk_spent']


            #assert kmins == expected_kmins, 's_w failed: got {}, expected {}'.format(kmins, expected_kmins)

            # TODO: check values of risk_goal/prob_stop
            #for rg_com, rg_exp in zip(risk_goal, expected_risk_expended):
            #    assert np.abs(rg_com - rg_exp) < error_level, 's_w failed: got {}, expected {}'.format(rg_com, rg_exp)
            #for i in range(len(risk_goal)):
            #    assert np.abs(risk_goal[i] - expected_risk_goal[i]) < error_level, 's_w failed: got {}, expected {}'.format(risk_goal[i], expected_risk_goal[i])


