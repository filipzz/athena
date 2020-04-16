"""Test rlacalc
Use hypothesis testing framework:
 https://hypothesis.readthedocs.io/en/latest/quickstart.html

TODO:
 Start with simple test
 Add failing test from Grant

"""

import sys
# TODO: get pytest working without this and without python3 -m pytest
#sys.path.insert(0, '/home/neal/py/projects/audit_cvrs/audit_cvrs')
import datetime
import logging
logging.basicConfig(filename='hypothesis-test.log', level=logging.DEBUG)
logging.debug("pytest run %s: path: %s" % (datetime.datetime.now(), sys.path))

from athena.audit import Audit

# logging.debug("raw nmin test: %s" % rlacalc.nmin(0.05, 1.03905, 0.02, 0, 0, 0, 0))

from hypothesis import given, settings, Verbosity, example, assume, note

import hypothesis.strategies as st

def make_audit(audit_type, alpha, delta, candidates, results, ballots_cast, winners, name, model, round_schedule):
    "Convenience function to make Audit instance with given election parameters"

    election = {
        "alpha": alpha,
        "delta": delta,
        "candidates": candidates,
        "results": results,
        "ballots_cast": ballots_cast,
        "winners": winners,
        "name": name,
        "model": model,
    }
    a = Audit(audit_type, election['alpha'], election['delta'])
    a.add_election(election)
    a.add_round_schedule(round_schedule)
    return a

def find_next_round_size(audit_type, alpha, delta, candidates, results, ballots_cast, winners, name, model, pstop_goal, round_schedule):
    "Convenience function to call a fresh Audit instance with given election parameters"

    election = {
        "alpha": alpha,
        "delta": delta,
        "candidates": candidates,
        "results": results,
        "ballots_cast": ballots_cast,
        "winners": winners,
        "name": name,
        "model": model,
        "pstop_goal": pstop_goal,
    }
    a = Audit(audit_type, election['alpha'], election['delta'])
    a.add_election(election)
    a.add_round_schedule(round_schedule)
    x = a.find_next_round_size(election['pstop_goal'])
    return x


def samplesizes(margin, pstop_goals, audit_type="ATHENA"):
    "Return sample sizes and other output given margin and stopping probability goals"

    assert 0.0 <= margin <= 1.0
    ballots_cast = 1000000
    margin_votes = round(margin * ballots_cast)
    b = ballots_cast//2 - margin_votes // 2
    a = b + int(margin_votes)
    results = [a, b]
    x = find_next_round_size(audit_type, 0.1, 1.0, ["A", "B"], results, ballots_cast, 1, "state", "bin", pstop_goals, [])
    return (x['detailed']['A-B']['next_round_sizes'][0], x)

# For the given limits, led by parameter examples, automate testing via hypothesis library
@given(st.floats(0.01, 1.0))
@settings(max_examples=10, deadline=10000) # deadline in milliseconds
@example(0.1)
def test_margins(margin):
    """Sanity tests with two stopping probabilities for a variety of margins."""

    pstop_goals = [0.7, 0.9]
    results = samplesizes(margin, pstop_goals)
    next_round_size_results = results[1]

    detailed = next_round_size_results['detailed']['A-B']
    nextroundsizes = detailed['next_round_sizes']
    prob_stop = detailed['prob_stop']
    i = 0
    logging.debug(f't1 stopping probability goal: {pstop_goals[i]} next round size: {nextroundsizes[i]} margin: {margin}')

    assert nextroundsizes[1] >= nextroundsizes[0]
    for goal, actual in zip(pstop_goals, prob_stop):
        assert actual >= goal

def next_round(a, winner_shares, r, pstop_goals):
    "Do another round in a multi-round audit"

    below_kmin = max(r['required']) - max(r['observed'])
    x = a.find_next_round_size(pstop_goals)
    incremental_round_sizes = list(map(lambda x: x - max(a.round_schedule) + 2 * below_kmin, x['future_round_sizes']))
    incremental_sample_size = incremental_round_sizes[0]
    a.add_round_schedule(a.round_schedule + [max(a.round_schedule) + incremental_sample_size])
    next_total_winner_share = a.round_schedule[-1] // 2
    winner_shares += [next_total_winner_share]
    message = f' Next round: draw {incremental_sample_size} more ballots, {next_total_winner_share - winner_shares[-2]} for winner'
    note(message)
    logging.debug(message)

    r = a.find_risk(winner_shares)
    logging.debug(f'  {r}')
    return r

# For the given limits, led by parameter examples, automate testing via hypothesis library
@given(st.floats(0.01, 1.0))
@settings(max_examples=10, deadline=100000) # deadline in milliseconds
@example(margin=0.784415)
@example(margin=0.7538450000000001)
@example(margin=0.8775250000000001)
@example(margin=0.9488450000000002)
@example(0.2)
def test_3_round_margins(margin):
    """Sanity tests with two stopping probabilities for a variety of margins."""

    assert 0.0 <= margin <= 1.0
    ballots_cast = 100000
    margin_votes = round(margin * ballots_cast)
    b = (ballots_cast - margin_votes) // 2
    a = b + margin_votes
    results = [a, b]

    note(f'Arguments to set it up: python3 athena.py -i -n hyp -b {" ".join(str(x) for x in results)}')

    assert sum(results) <= ballots_cast

    audit_type = "ATHENA"
    alpha = 0.1
    delta = 1.0
    candidates = ["A", "B"]
    ballots_cast = 100000
    winners = 1
    name = "test_election"
    model = "bin"
    pstop_goals = [.7, .9]
    round_schedule = []

    i = 0
    logging.debug(f't3 stopping probability goal: {pstop_goals[i]} margin: {margin} res: {results}')

    a = make_audit(audit_type, alpha, delta, candidates, results, ballots_cast, winners, name, model, round_schedule)

    next_round_size_results = a.find_next_round_size(pstop_goals)

    # Use the round size required for the first stopping probability
    sample_size = next_round_size_results['future_round_sizes'][0]
    a.add_round_schedule([sample_size])

    # Say the sample is a tie, i.e. not enough to finish the audit
    winner_shares = [sample_size // 2]
    r = a.find_risk(winner_shares)

    message = f' draw {sample_size} ballots, {winner_shares[-1]} for winner'
    note(message)
    logging.debug(message)

    # Report and check results
    detailed = next_round_size_results['detailed']['A-B']
    nextroundsizes = detailed['next_round_sizes']
    actual_prob_stop = detailed['prob_stop']

    assert nextroundsizes[1] >= nextroundsizes[0]
    for goal, actual in zip(pstop_goals, actual_prob_stop):
        assert actual >= goal

    r = next_round(a, winner_shares, r, pstop_goals)
    r = next_round(a, winner_shares, r, pstop_goals)

test_3_round_margins()
test_margins()

def test_single_round():
    audit_type = "ATHENA"
    alpha = 0.1
    delta = 1.0
    candidates = ["A", "B"]
    results = [60000, 40000]
    ballots_cast = 100000
    winners = 1
    name = "test_election"
    model = "bin"
    pstop_goal = [.7, .9]
    round_schedule = []

    a = make_audit(audit_type, alpha, delta, candidates, results, ballots_cast, winners, name, model, round_schedule)
    x = a.find_next_round_size(pstop_goal)
    i = 0
    nextroundsizes = x['detailed']['A-B']['next_round_sizes']
    logging.debug(f'results: {a.election.results} pstop {pstop_goal[i]} next round {nextroundsizes[i]}')
    assert nextroundsizes[1] >= nextroundsizes[0]

test_single_round()
