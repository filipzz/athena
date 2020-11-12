from json import load
from os import path

from athena.audit import Audit
#from athena.contest import Contest


def test_first_round_sizes():

    error_level = 0.0001

    # file with the definition of test
    with open(path.join(path.dirname(__file__),'test_def_next_round.json'), 'r') as f:
        test_info = load(f)

    for test_list in test_info:
        election_file = test_info[test_list]["election_file"]
        audit_file = test_info[test_list]["audit_file"]

        with open(path.join(path.dirname(__file__),election_file), 'r') as f:
            elections = load(f)

        with open(path.join(path.dirname(__file__),audit_file), 'r') as f:
            tests = load(f)


        type_of_test = "next_round_size"
        #for type_of_test in tests.keys():
        #print("Test parameters:")
        #print(str(tests[type_of_test]["params"]))
        #print("test type: " + type_of_test)
        #print(str(tests[type_of_test]))



        for test in tests[type_of_test]:

            if test in {"params"}:
                print("Test parameters are:")
                print(str(tests[type_of_test]["params"]))
            else:

                print(str(test))

                info = tests[type_of_test][test]
                print("info:" + str(info))

                print(str(elections[info["election"]]))

                if "delta" in info:
                    w = Audit(info["audit_type"], info["alpha"], info["delta"])
                else:
                    w = Audit(info["audit_type"], info["alpha"])

                #w.add_election(elections[info["election"]]["contests"][info["contest"]])
                election_data = elections[info["election"]]
                rs = election_data['contests']['presidential']['results']
                results = [max(rs), min(rs)]

                w.add_election(w.set_ele(results))
                w.load_contest('x')
                results = w.predict_round_sizes(info['quants'])
                print(str(results))
                #w.load_contest()

                #if "round_schedule" in info:
                #    w.add_round_schedule(info["round_schedule"])
                #    w.add_observations(info["round_observations"])

                #x = w.find_next_round_size(info["quants"])
                #print(str(x))

                expected = info['expected']
                expected_round_sizes = expected["round_candidates"]
                #expected_kmins = expected['kmins']
                #expected_risk_expended = expected['risk_expended']

                computed = []
                for t in results:
                    computed.append(t[-1])


                #assert x["future_round_sizes"] == expected_round_sizes, 's_w failed: got {}, expected {}'.format(x["future_round_sizes"], expected_round_sizes)
                assert computed == expected_round_sizes, 's_w failed: got {}, expected {}'.format(computed, expected_round_sizes)
                # TODO: check values of risk_goal/prob_stop
                #for rg_com, rg_exp in zip(risk_goal, expected_risk_expended):
                #    assert np.abs(rg_com - rg_exp) < error_level, 's_w failed: got {}, expected {}'.format(rg_com, rg_exp)

                del w


def test_first_round_sizes():

    error_level = 0.0001

    # file with the definition of test
    with open(path.join(path.dirname(__file__),'test_def_next_round.json'), 'r') as f:
        test_info = load(f)

    for test_list in test_info:
        election_file = test_info[test_list]["election_file"]
        audit_file = test_info[test_list]["audit_file"]

        with open(path.join(path.dirname(__file__),election_file), 'r') as f:
            elections = load(f)

        with open(path.join(path.dirname(__file__),audit_file), 'r') as f:
            tests = load(f)


        type_of_test = "next_round_size"
        #for type_of_test in tests.keys():
        #print("Test parameters:")
        #print(str(tests[type_of_test]["params"]))
        #print("test type: " + type_of_test)
        #print(str(tests[type_of_test]))



        for test in tests[type_of_test]:

            if test in {"params"}:
                print("Test parameters are:")
                print(str(tests[type_of_test]["params"]))
            else:

                print(str(test))

                info = tests[type_of_test][test]
                print("info:" + str(info))

                print(str(elections[info["election"]]))

                if "delta" in info:
                    w = Audit(info["audit_type"], info["alpha"], info["delta"])
                else:
                    w = Audit(info["audit_type"], info["alpha"])

                #w.add_election(elections[info["election"]]["contests"][info["contest"]])
                election_data = elections[info["election"]]
                rs = election_data['contests']['presidential']['results']
                results = [max(rs), min(rs)]

                w.add_election(w.set_ele(results))
                w.load_contest('x')
                results = w.predict_round_sizes(info['quants'])
                print(str(results))
                #w.load_contest()

                #if "round_schedule" in info:
                #    w.add_round_schedule(info["round_schedule"])
                #    w.add_observations(info["round_observations"])

                #x = w.find_next_round_size(info["quants"])
                #print(str(x))

                expected = info['expected']
                expected_round_sizes = expected["round_candidates"]
                #expected_kmins = expected['kmins']
                #expected_risk_expended = expected['risk_expended']

                computed = []
                for t in results:
                    computed.append(t[-1])



                #assert x["future_round_sizes"] == expected_round_sizes, 's_w failed: got {}, expected {}'.format(x["future_round_sizes"], expected_round_sizes)
                assert computed == expected_round_sizes, 's_w failed: got {}, expected {}'.format(computed, expected_round_sizes)
                # TODO: check values of risk_goal/prob_stop
                #for rg_com, rg_exp in zip(risk_goal, expected_risk_expended):
                #    assert np.abs(rg_com - rg_exp) < error_level, 's_w failed: got {}, expected {}'.format(rg_com, rg_exp)

                del w
