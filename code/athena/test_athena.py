import json
import os

from athena.athena import AthenaAudit
import numpy as np


def test_find_kmins():

    error_level = 0.0001

    with open(os.path.join(os.path.dirname(__file__),'test_data.json'), 'r') as f:
    #with open('athena/test_data.json', 'r') as f:
        tests = json.load(f)

    type_of_test = "find_kmins"
    #for type_of_test in tests.keys():
    print("test type: " + type_of_test)
    for test in tests[type_of_test]:
        expected = tests[type_of_test][test]['expected']
        nn = tests[type_of_test][test]['nn']
        wd = tests[type_of_test][test]['wd']
        alpha = tests[type_of_test][test]['alpha']
        round_schedule = tests[type_of_test][test]['round_schedule']
        audit_type = tests[type_of_test][test]['audit_type']
        expected_kmins = expected['kmins']
        expected_risk_expended = expected['risk_expended']

        margin = (2 * wd - nn)/nn
        gamma = 1

        print("\n" + test + "\t" + str(nn) + "\t" + str(wd) + "\t" + str(round_schedule))

        #computed = schedule.find_new_kmins(nn, wd, alpha, round_schedule, risk_goal)
        audit_object = AthenaAudit()
        if audit_type.lower() == "bravo" or audit_type.lower() == "wald":
            computed = audit_object.bravo(margin, alpha, round_schedule)
        elif audit_type.lower() == "arlo":
            computed = audit_object.arlo(margin, alpha, round_schedule)
        else:
            computed = audit_object.athena(margin, alpha, gamma, round_schedule)

        kmins = computed["kmins"]
        prob_sum = computed["prob_sum"]
        prob_tied_sum = computed["prob_tied_sum"]
        gammas = computed["gammas"]

        print(computed)
        #kmins = computed['kmin_new']
        risk_goal = prob_tied_sum #computed['risk_spent']

        assert kmins == expected_kmins, 's_w failed: got {}, expected {}'.format(kmins, expected_kmins)

        # TODO: check values of risk_goal/prob_stop
        for rg_com, rg_exp in zip(risk_goal, expected_risk_expended):
            assert np.abs(rg_com - rg_exp) < error_level, 's_w failed: got {}, expected {}'.format(rg_com, rg_exp)



