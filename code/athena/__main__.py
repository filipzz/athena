import sys
import argparse
import string
import logging
import json
import math

from athena.contest import Contest
from athena.audit import Audit
from athena.athena import AthenaAudit

if __name__ == '__main__':

    info_text = 'This program lets for performing ATHENA audit. \n' \
                'There are two main use cases:\n' \
                '\t(1) find out how many ballots need to be drawn at random to complete audit with e.g., 90%:\n' \
                '\t\tpython -m athena --name contestName --ballots 5000 3000 --pstop .9\n' \
                'where: --ballots 5000 3000 corresponds to number of ballots each candidate got, -' \
                '-pstop is the desired stopping probability' \
                '\t(2) when a certain number of ballots is drawn, evaluate the p-value:\n' \
                '\t\tpython -m athena --name contestName --ballots 5000 3000 --rounds 120 --risk 70\n' \
                'where --rounds 120 means that 120 relevant ballots were drawn and --risk 70 means that 70 of ' \
                'them were for the winner and one wants to evaluate the p-value'

    parser = argparse.ArgumentParser(description=info_text)
    parser.add_argument("-v", "-V", "--version", help="shows program version", action="store_true")
    parser.add_argument("-a", "--alpha", help="set alpha (risk limit) for the election", type=float, default=0.1)
    parser.add_argument("-b", "--ballots", help="set the list of ballots cast for every candidate", nargs="*", type=int)
    parser.add_argument("-c", "--candidates", help="set the candidate list (names)", nargs="*")
    parser.add_argument("-d", "--debuglevel", type=int, default=logging.WARNING,
                        help="Set logging level to debuglevel, expressed as an integer: "
                        "DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50. "
                        "The default is %(default)s" )
    parser.add_argument("-e", "--risk", "--evaluate_risk", help="evaluate risk for given audit results", nargs="+",
                        type=int)
    parser.add_argument("-f", "--file", help="read data from the file")
    parser.add_argument("-g", "--delta", help="set delta (upset limit) for the audit", type=float, default=1.0)
    parser.add_argument("-i", "--interactive", help="sets mode to interactive", const=1, default=0, nargs="?")
    parser.add_argument("-n", "--name", help="sets election name")
    parser.add_argument("-N", "--new", "--new", help="sets election name")
    parser.add_argument("-p", "--pstop", help="set stopping probability goals for each round "
                                              "(corresponding round schedule will be found)", nargs="+", type=float)
    parser.add_argument("-r", "--rounds", "--round_schedule", help="set the round schedule", nargs="+", type=int)
    parser.add_argument("-t", "--total", help="set the total number of ballots in given contest", type=int)
    parser.add_argument("-w", "--winners", help="set number of winners for the given race", type=int, default=1)
    parser.add_argument("--type", help="set the audit type (athena/bravo/arlo/minerva/metis)", default="athena")
    parser.add_argument("--conv", help="sets method for convolutions either default or fft", default='fft')
    parser.add_argument("--approx", help="sets approximation threshold for binary search/approximation for next round size", type=float, default=0.015)

    args, args_unknown = parser.parse_known_args()

    logging.basicConfig(level=args.debuglevel)

    audit_type = "ATHENA"
    alpha = 0.1
    mode = ""
    ballots_cast = 0
    candidates = []
    results = []
    contest_name = ""
    winners = 1
    mode_rounds = ""
    name = ""

    if args.version:
        print("ATHENA-RLA version 0.7.1")
    if (args.new is not None) or (args.name is not None):
        mode = "new"
        if args.new:
            name = args.new
            contest_name = args.new

        if args.name:
            name = args.name
            contest_name = args.name

        if args.alpha:
            alpha = args.alpha
            if alpha < 0.0 or alpha >= 0.5:
                print("Value of alpha is incorrect")
                sys.exit(2)

        delta = args.delta
        if delta < 0.0:
            print("Value of camma is not correct")
            sys.exit(2)

        if args.type:
            if (args.type).lower() in {"bravo", "wald"}:
                audit_type = "bravo"
            elif (args.type).lower() == "arlo":
                audit_type = "arlo"
            elif (args.type).lower() in {"minerva", "anat", "neith", "sulis"}:
                audit_type = "minerva"
            elif (args.type).lower() in {"metis"}:
                audit_type = "metis"
            else:
                audit_type = "athena"

        if args.ballots:
            results = args.ballots
            if args.total:
                ballots_cast = args.total
                if ballots_cast < sum(results):
                    print("Incorrect number of total ballots cast")
                    sys.exit(2)
            else:
                ballots_cast = sum(results)
        elif args.file:
            file_name = args.file
            mode = "read"
        else:
            print("Missing -b / --ballots argument")
            sys.exit(2)

        if args.candidates:
            candidates = args.candidates
            if len(args.candidates) != len(args.ballots):
                print("Number of candidates does not match number of results")
                sys.exit(2)
        elif mode == "read":
            pass
        else:
            assert len(args.ballots) <= 26
            candidates = [string.ascii_uppercase[i] for i in range(len(args.ballots))]

        if args.pstop:
            if args.rounds:
                round_schedule = args.rounds
                pstop_goal = []
                if max(round_schedule) > ballots_cast:
                    print("Round schedule is incorrect")
                    sys.exit(2)

            mode_rounds = "pstop"
            pstop_goal = args.pstop
            if not args.rounds:
                round_schedule = []
            #print(str(pstop_goal))

        elif args.interactive:
            pstop_goal = []
            if args.rounds:
                round_schedule = args.rounds
                if max(round_schedule) > ballots_cast:
                    print("Round schedule is incorrect")
                    sys.exit(2)

            mode_rounds = "interactive"

            if not args.rounds:
                round_schedule = []

        elif args.rounds:
            mode_rounds = "rounds"
            round_schedule = args.rounds
            pstop_goal = []
            #if max(round_schedule) > ballots_cast:
            #    print("Round schedule is incorrect")
            #    sys.exit(2)
        elif mode == "read":
            pass
        else:
            print("Missing -r / --rounds argument")
            sys.exit(2)

        if mode != "read" and args.winners:
            winners = args.winners
            if winners >= len(candidates):
                print("There is nothing to audit - every candidate is a winner.")
                sys.exit(2)

        if args.risk:
            mode_rounds = "risk"
            actual_kmins = args.risk
            if len(candidates) > 2:
                print("Current version supports only 2-candidate race for risk estimation")
                sys.exit(2)

        convolve_method = 'direct'
        if args.conv:
            if args.conv == 'fft':
                convolve_method = 'fft'

        if 0.0 < args.approx < 1.0:
            approximation_threshold = args.approx
        else:
            approximation_threshold = 0.015

    #elif args.load:
    #    mode = "read"
    else:
        print("Call python -m athena -h for help")

    model = "bin"


    election = {}
    election["alpha"] = alpha
    #election["delta"] = delta
    election["name"] = name
    election["model"] = model
    #election["pstop"] = pstop_goal
    #election["round_schedule"] = round_schedule
    save_to = "elections/" + name

    if mode == "read":
        election_object = Contest(election)
        #election_object.read_from_file(file_name, contest_name)
        election_object.read_election_data(file_name)
        election_object.load_contest_data(contest_name)
        election_object.print_election()
        candidates = election_object.candidates
        election["candidates"] = candidates
        ballots_cast = election_object.ballots_cast
        election["ballots_cast"] = ballots_cast
        results = election_object.results
        election["results"] = results
        election["winners"] = 1
    else:
        election["ballots_cast"] = ballots_cast
        election["total_ballots"] = ballots_cast
        tally = {}
        for can, votes in zip(candidates, results):
            tally[can] = votes
        tallyj = json.dumps(tally)
        #election["contests"] = f'{{"{contest_name}": {{"contest_ballots": {ballots_cast}, "tally": {tallyj}, "num_winners": {winners}, "reported_winners": ["A"]}} }}'
        #election["data"] = f'{{"name": "x", "total_ballots": {ballots_cast}, "contests" : {election["contests"]}}}'
        election["contests"] = {contest_name: {"contest_ballots": ballots_cast, "tally": tally, "num_winners": winners, "reported_winners": ["A"]}}
        election["data"] = {"name": "x", "total_ballots": ballots_cast, "contests" : election["contests"]}
        #print(election["contests"])
        #json.loads(election["contests"])
        #print(election["data"])
        #print(election["data"])
        election["candidates"] = candidates
        election["results"] = results
        election["winners"] = winners

        #print(json.loads(election["contests"]))

        #print("Candidates: ", candidates)

        election_object = Contest(election)
        #election_object.load_contest_data("x", election["data"])

        #tools.print_election(election)

    #for election[""]
    #print(election)
    #election_object.print_election()

    #print(election)

    #print("Round schedule: " + str(round_schedule))

    if mode_rounds == "rounds":
        #w = Audit(audit_type, alpha)
        #w.add_election(w.set_ele())
        #print(str(election))
        #print(election_object)

        w = AthenaAudit(audit_type.lower(), alpha, delta)
        w.set_convolve_method(convolve_method)
        w.set_approximation_threshold(approximation_threshold)
        #print(str(w))
        #for i in range(len(candidates)):
        #print("option temporary unavailable")
        """ # temporary commented out """
        for i in election_object.declared_winners:
            ballots_i = results[i]
            candidate_i = candidates[i]
            #for j in range(i + 1, len(candidates)):
            for j in election_object.declared_losers:
                ballots_j = results[j]
                candidate_j = candidates[j]

                print("\n\n%s (%s) vs %s (%s)" % (candidate_i, (ballots_i), candidate_j, (ballots_j)))
                bc = ballots_i + ballots_j
                winner = max(ballots_i, ballots_j)
                print("\tmargin:\t" + str((winner - min(ballots_i, ballots_j))/bc))
                rs = []

                for x in round_schedule:
                    y = math.floor(x * bc / ballots_cast)
                    rs.append(y)

                margin = (2 * winner - bc)/bc

                audit_object = AthenaAudit(audit_type.lower(), alpha, delta)
                audit_object.set_convolve_method(convolve_method)
                audit_object.set_approximation_threshold(approximation_threshold)
                audit_athena = audit_object.audit(margin, rs)

                #print(str(audit_object))
                kmins = audit_athena["kmins"]
                prob_sum = audit_athena["prob_sum"]
                prob_tied_sum = audit_athena["prob_tied_sum"]
                deltas = audit_athena["deltas"]
                #expected = list(map(lambda x: math.floor(x * winner/bc), round_schedule))

                print("\n\tApprox round schedule:\t" + str(rs))
                #print("\tExpected for winner:\t%s" % (str(expected)))
                print("\t%s kmins:\t\t%s" % (audit_type, str(kmins)))
                print("\t%s pstop cumul (audit):\t%s" % (audit_type, str(prob_sum)))
                print("\t%s pstop cumul (tied): \t%s" % (audit_type, str(prob_tied_sum)))

                prob_sum_ex = [0] + prob_sum
                prob_tied_sum_ex = [0] + prob_tied_sum
                prob_sum_round = [(prob_sum_ex[i+1]-prob_sum_ex[i]) for i in range(len(prob_sum))]
                prob_tied_sum_round = [(prob_tied_sum_ex[i+1]-prob_tied_sum_ex[i]) for i in range(len(prob_tied_sum))]
                print("\t%s pstop round (audit):\t%s" % (audit_type, str(prob_sum_round)))
                print("\t%s pstop round (tied): \t%s" % (audit_type, str(prob_tied_sum_round)))

                if w.audit_type.lower in {"arlo", "bravo", "athena"}:
                    true_risk = []
                    for p, pt in zip(prob_sum, prob_tied_sum):
                        if p == 0:
                            true_risk.append(0.0)
                        else:
                            true_risk.append(pt/p)

                    print("\t%s deltas ():\t%s" % (audit_type, str(deltas)))
                    print("\t%s ratio:\t%s" % (audit_type, str(true_risk)))
            """ """

    elif mode_rounds == "pstop":

        if mode == "read":
            w = Audit(audit_type, alpha)
            w.set_colvolve_method(convolve_method)
            w.set_approximation_threshold(approximation_threshold)
            w.read_election_results(file_name)
            w.load_contest(contest_name)
            w.add_round_schedule(round_schedule)
            #print("ele-d", w.election.data)
            #print(w.data)
            #print(w.contests)
            #print(w.contest_list)
            #w.election.print_election()
            print(w.predict_round_sizes(pstop_goal))
        else:
            w = Audit(audit_type, alpha, delta)
            w.set_colvolve_method(convolve_method)
            w.set_approximation_threshold(approximation_threshold)
            #print(election)
            w.add_election(election)
            w.load_contest(contest_name)
            w.add_round_schedule(round_schedule)
            #print(election)
            #print("ele-d", w.election.data)
            #print(w.data)
            #print(w.contests)
            #print(round_schedule)
            #x = w.find_next_round_size(pstop_goal)
            x = w.predict_round_sizes(pstop_goal)
            print(str(x))


    elif mode_rounds == "interactive":


        if mode == "read":
            w = Audit(audit_type)
            w.set_colvolve_method(convolve_method)
            w.set_approximation_threshold(approximation_threshold)
            w.read_election_results(file_name)
            w.load_contest(contest_name)
        else:
            w = Audit(audit_type, alpha, delta)
            w.set_colvolve_method(convolve_method)
            w.set_approximation_threshold(approximation_threshold)
            w.add_election(election)
            w.load_contest(contest_name)
            w.add_round_schedule(round_schedule)

        w.run_interactive()

    if mode_rounds == "risk":

        if mode == "read":
            w = Audit(audit_type)
            w.set_colvolve_method(convolve_method)
            w.set_approximation_threshold(approximation_threshold)
            w.read_election_results(file_name)
            w.load_contest(contest_name)
        else:
            w = Audit(audit_type, alpha, delta)
            w.set_colvolve_method(convolve_method)
            w.set_approximation_threshold(approximation_threshold)
            w.add_election(election)
            w.load_contest(contest_name)

        print(contest_name)

        for i, round_i, ballots_i in zip(range(len(actual_kmins)), round_schedule, actual_kmins):
            #w.add_round_schedule(round_schedule)
            if i == 0:
                #w.add_observations(round_i, [ballots_i, round_i - ballots_i])
                #w.add_observations([ballots_i, round_i - ballots_i])
                w.set_observations(round_i, round_i, [ballots_i, round_i - ballots_i])
            else:
                round_size = round_i - round_schedule[i-1]
                ballots_now = ballots_i - actual_kmins[i-1]
                #w.add_observations(round_size, [ballots_now, round_size - ballots_now])
                #w.add_observations([ballots_now, round_size - ballots_now])
                w.set_observations(round_size, round_size, [ballots_now, round_size - ballots_now])

            #w.present_state()
            #print(w.status)

        print(w.get_pval(contest_name))
        #x = w.find_risk(actual_kmins)
        #x = w.find_risk()
        #print(str(x))

