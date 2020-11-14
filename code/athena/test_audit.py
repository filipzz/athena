from json import load
from os import path

from athena.audit import Audit
#from athena.athena import AthenaAudit

from numpy import abs

#from athena.election import Election


def set_ele(results):
    election = {}
    #election["alpha"] = risk_limit
    election["delta"] = 1.0
    election["name"] = "name"
    contest_name = "pres"
    #election["round_schedule"] = round_schedule
    ballots_cast = sum(results)
    election["ballots_cast"] = ballots_cast
    election["total_ballots"] = ballots_cast
    candidates = ["A", "B"]
    #results = {1981473, 95369}
    tally = {}
    for can, votes in zip(candidates, results):
        tally[can] = votes

    #tallyj = json.dumps(tally)
            #election["contests"] = f'{{"{contest_name}": {{"contest_ballots": {ballots_cast}, "tally": {tallyj}, "num_winners": {winners}, "reported_winners": ["A"]}} }}'
            #election["data"] = f'{{"name": "x", "total_ballots": {ballots_cast}, "contests" : {election["contests"]}}}'
    election["contests"] = {contest_name: {"contest_ballots": ballots_cast, "tally": tally, "num_winners": 1, "reported_winners": ["A"]}}
    election["data"] = {"name": "x", "total_ballots": ballots_cast, "contests" : election["contests"]}
            #print(election["contests"])
            #json.loads(election["contests"])
            #print(election["data"])
            #print(election["data"])
    election["candidates"] = candidates
    election["results"] = results
    election["winners"] = ["A"]
    #election_object = Contest(election["data"])
    #return election_object
    #print(str(election))
    return election

def test_find_kmins():

    error_level = 0.0001

    with open(path.join(path.dirname(__file__),'test_data/full_test.json'), 'r') as f:
        list_of_files = load(f)


    for file in list_of_files["files"]:

        with open(path.join(path.dirname(__file__),'test_data/', file), 'r') as f:
        #with open('athena/test_data.json', 'r') as f:
            tests = load(f)

        list_of_tests = tests.keys()
        print(str(list_of_tests))
        #type_of_test = "find_kmins"
        #for type_of_test in tests.keys():
        for test_name in tests.keys():
            election_data = tests[test_name]["election"]
            alpha = tests[test_name]["alpha"]
            audit_type = tests[test_name]["audit_type"]

            w = Audit(audit_type, alpha)
            w.add_election(election_data)

            for round_number in tests[test_name]["rounds"]:

                for method_tested in tests[test_name]["rounds"][round_number]:
                    params = tests[test_name]["rounds"][round_number][method_tested]

                    contest_name = params["contest"]
                    w.load_contest(contest_name)

                    """testing find_next_round_sizes"""
                    if method_tested == 'find_next_round_sizes':
                        quants = params["quants"]
                        computed = w.predict_round_sizes(quants)
                        for res, exp in zip(computed, params["expected"]["round_candidates"]):
                            size = res[-1]
                            assert size == exp, ' find_next_round_sizes failed: got {}, expected {}'.format(size, exp)

                    if method_tested == 'pvalue':
                        observations = params["observations"]
                        total = sum(observations)
                        w.set_observations(total, total, observations)
                        computed = w.get_pval(contest_name)
                        exp = params["expected"]["pvalue"]
                        #if exp is float('inf'):
                        assert computed == exp or abs(computed - exp) < error_level, "pvalue failed: got {}, expected {}".format(computed, exp)

                        #part for pairwise
                        if "pairwise" in params["expected"]:
                            computed_full = w.status[contest_name].get_pairwise()

                            for exxp, ress in zip(params["expected"]["pairwise"], computed_full[0]):
                                expected_risk = params["expected"]["pairwise"][exxp]
                                computed_risk = computed_full[0][ress]["risk"]
                                assert computed_risk == expected_risk or abs(computed_risk - expected_risk) < error_level, "pvalue failed for {}: got {}, expected {}".format(
                                    exxp, computed_risk, expected_risk)

