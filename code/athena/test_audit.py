import json
import os

#from athena.election import Election
from athena.audit import Audit
import numpy as np


def test_next_rounds():

    error_level = 0.0001

    with open(os.path.join(os.path.dirname(__file__),'test_election.json'), 'r') as f:
        elections = json.load(f)

    with open(os.path.join(os.path.dirname(__file__),'test_audit.json'), 'r') as f:
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


        x = w.find_next_round_size(info["quants"])
        print(str(x))

        expected = info['expected']
        expected_round_sizes = expected["round_candidates"]
        #expected_kmins = expected['kmins']
        #expected_risk_expended = expected['risk_expended']


        assert x["future_round_sizes"] == expected_round_sizes, 's_w failed: got {}, expected {}'.format(kmins, expected_kmins)

        # TODO: check values of risk_goal/prob_stop
        #for rg_com, rg_exp in zip(risk_goal, expected_risk_expended):
        #    assert np.abs(rg_com - rg_exp) < error_level, 's_w failed: got {}, expected {}'.format(rg_com, rg_exp)

        del w



