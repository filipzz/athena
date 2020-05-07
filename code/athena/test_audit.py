import json
import os

#from athena.election import Election
from athena.audit import Audit
import numpy as np


def test_next_rounds():

    error_level = 0.0001

    # file with the definition of test
    with open(os.path.join(os.path.dirname(__file__),'test_def.json'), 'r') as f:
        test_info = json.load(f)

    for test_list in test_info:
        election_file = test_info[test_list]["election_file"]
        audit_file = test_info[test_list]["audit_file"]

        with open(os.path.join(os.path.dirname(__file__),election_file), 'r') as f:
            elections = json.load(f)

        with open(os.path.join(os.path.dirname(__file__),audit_file), 'r') as f:
            tests = json.load(f)


        type_of_test = "next_round_size"
        #for type_of_test in tests.keys():
        print("test type: " + type_of_test)
        for test in tests[type_of_test]:

            print(str(test))

            info = tests[type_of_test][test]
            print(str(info))

            if "delta" in info:
                w = Audit(info["audit_type"], info["alpha"], info["delta"])
            else:
                w = Audit(info["audit_type"], info["alpha"])

            w.add_election(elections[info["election"]]["contests"][info["contest"]])

            if "round_schedule" in info:
                w.add_round_schedule(info["round_schedule"])
                w.add_observations(info["round_observations"])

            x = w.find_next_round_size(info["quants"])
            print(str(x))

            expected = info['expected']
            expected_round_sizes = expected["round_candidates"]
            #expected_kmins = expected['kmins']
            #expected_risk_expended = expected['risk_expended']


            assert x["future_round_sizes"] == expected_round_sizes, 's_w failed: got {}, expected {}'.format(x["future_round_sizes"], expected_round_sizes)

            # TODO: check values of risk_goal/prob_stop
            #for rg_com, rg_exp in zip(risk_goal, expected_risk_expended):
            #    assert np.abs(rg_com - rg_exp) < error_level, 's_w failed: got {}, expected {}'.format(rg_com, rg_exp)

            del w


def test_evaluate_risk():

    error_level = 0.0001

    # file with the definition of test
    with open(os.path.join(os.path.dirname(__file__),'test_def.json'), 'r') as f:
        test_info = json.load(f)

    for test_list in test_info:
        election_file = test_info[test_list]["election_file"]
        audit_file = test_info[test_list]["audit_file"]

        with open(os.path.join(os.path.dirname(__file__),election_file), 'r') as f:
            elections = json.load(f)

        with open(os.path.join(os.path.dirname(__file__),audit_file), 'r') as f:
            tests = json.load(f)


        type_of_test = "evaluate_risk"

        print("test type: " + type_of_test)
        for test in tests[type_of_test]:

            print(str(test))

            info = tests[type_of_test][test]
            print(str(info))

            if "delta" in info:
                w = Audit(info["audit_type"], info["alpha"], info["delta"])
            else:
                w = Audit(info["audit_type"], info["alpha"])

            w.add_election(elections[info["election"]]["contests"][info["contest"]])

            if "round_schedule" in info:
                w.add_round_schedule(info["round_schedule"])

            #x = w.find_risk(info["audit_observations"])
            w.add_observations(info["audit_observations"])
            x = w.find_risk()
            print(str(x))

            expected = info['expected']
            passed = expected["passed"]
            pvalue = expected["pvalue"]
            delta = expected["delta"]

            assert x["passed"] == passed, 's_w failed: got {}, expected {}'.format(x["passed"], passed)

            # TODO: check values of risk_goal/prob_stop
            #for rg_com, rg_exp in zip(risk_goal, expected_risk_expended):
            assert np.abs(x["delta"] - delta) < error_level, 's_w failed: got {}, expected {}'.format(x["delta"], delta)
            assert np.abs(x["risk"] - pvalue) < error_level, 's_w failed: got {}, expected {}'.format(x["risk"], risk)

            del w

