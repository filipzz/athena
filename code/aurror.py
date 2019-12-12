import sys, argparse
import string
from scipy.stats import binom
import math
import tools


def next_round_prob(margin, round_size_prev, round_size, kmin, prob_table_prev):
    prob_table = [0] * (round_size + 1)
    for i in range(kmin + 1):
        for j in range(round_size + 1):
            prob_table[j] = prob_table[j] + binom.pmf(j-i, round_size - round_size_prev, (1+margin)/2) * prob_table_prev[i]

    return prob_table

def aurror(margin, alpha, round_schedule):
    round_schedule = [0] + round_schedule
    number_of_rounds = len(round_schedule)
    prob_table_prev = [1]
    prob_tied_table_prev = [1]
    kmins = [0] * number_of_rounds
    prob_sum = [0] * number_of_rounds
    prob_tied_sum = [0] * number_of_rounds

    for round in range(1,number_of_rounds):
        prob_table = next_round_prob(margin, round_schedule[round - 1], round_schedule[round], kmins[round - 1], prob_table_prev)
        prob_tied_table = next_round_prob(0, round_schedule[round - 1], round_schedule[round], kmins[round - 1], prob_tied_table_prev)

        kmin_found = False
        kmin_candidate = math.floor(round_schedule[round]/2)
        while kmin_found == False and kmin_candidate <= round_schedule[round]:
            if alpha * (sum(prob_table[kmin_candidate:len(prob_table)]) + prob_sum[round - 1]) >= (sum(prob_tied_table[kmin_candidate:len(prob_tied_table)]) + prob_tied_sum[round - 1]):
                kmin_found = True
                kmins[round] = kmin_candidate
                prob_sum[round] = sum(prob_table[kmin_candidate:len(prob_table)]) + prob_sum[round - 1]
                prob_tied_sum[round] = sum(prob_tied_table[kmin_candidate:len(prob_tied_table)]) + prob_tied_sum[round - 1]
            else:
                kmin_candidate = kmin_candidate + 1

        # cleaning prob_table/prob_tied_table
        for i in range(kmin_candidate, round_schedule[round] + 1):
            prob_table[i] = 0
            prob_tied_table[i] = 0

        prob_table_prev = prob_table
        prob_tied_table_prev = prob_tied_table

    return {"kmins" : kmins[1:len(kmins)], "prob_sum" : prob_sum[1:len(prob_sum)], "prob_tied_sum" : prob_tied_sum[1:len(prob_tied_sum)]}




if (__name__ == '__main__'):

    info_text = 'This program lets for computing AURROR parameters.'
    parser = argparse.ArgumentParser(description=info_text)
    parser.add_argument("-v","-V", "--version", help="shows program version", action="store_true")
    parser.add_argument("-n", "--new", help="creates new election folder where all data are stored")
    parser.add_argument("-a", "--alpha", help="set alpha (risk limit) for the election", type=float, default=0.1)
    parser.add_argument("-c", "--candidates", help="set the candidate list (names)", nargs="*")
    parser.add_argument("-b", "--ballots", help="set the list of ballots cast for every candidate", nargs="*", type=int)
    parser.add_argument("-t", "--total", help="set the total number of ballots in given contest", type=int)
    parser.add_argument("-r", "-rs", "--rounds", "--round_schedule", help="set the round schedule", nargs="+", type=int)
    parser.add_argument("-p", "--pstop", help="set stopping probability goals for each round (corresponding round schedule will be found)", nargs="+", type=float)
    parser.add_argument("-w", "--winners", help="set number of winners for the given race", type=int, default=1)
    parser.add_argument("-l", "--load", help="set the election to read")
    parser.add_argument("-e", "--risk", "--evaluate_risk", help="evaluate risk for given audit results", nargs="+", type=int)
    args = parser.parse_args()

    if args.version:
        print("AURROR version 0.2")
    if args.new:
        mode = "new"
        name = args.new

        alpha = args.alpha
        if alpha < 0.0 or alpha > 1.0:
            print("Value of alpha is incorrect")
            sys.exit(2)

        if args.ballots:
            results = args.ballots
            if args.total:
                ballots_cast = args.total
                if ballots_cast < sum(results):
                    print("Incorrect number of total ballots cast")
                    sys.exit(2)
            else:
                ballots_cast = sum(results)
        else:
            print("Missing -b / --ballots argument")
            sys.exit(2)

        if args.candidates:
            candidates = args.candidates
            if len(args.candidates) != len(args.ballots):
                print("Number of candidates does not match number of results")
                sys.exit(2)
        else:
            assert len(args.ballots) <= 26
            candidates = [string.ascii_uppercase[i] for i in range(len(args.ballots))]

        if args.rounds:
            mode_rounds = "rounds"
            round_schedule = args.rounds
            pstop_goal = []
            if max(round_schedule) > ballots_cast:
                print("Round schedule is incorrect")
                sys.exit(2)
        elif args.pstop:
            mode_rounds = "goal"
            pstop_goal = args.pstop
            round_schedule = []
        else:
            print("Missing -r / --rounds argument")
            sys.exit(2)




        if args.winners:
            winners = args.winners
            if winners >= len(candidates):
                print("There is nothing to audit - every candidate is a winner.")
                sys.exit(2)

        eval_risk = ""
        if args.risk:
            #if len(args.risk) <= len(args.ballots):
            eval_risk = "true"
            actual_kmins = args.risk
            #else:
            #    print("Number of results is larger than the number of rounds.")
            #    sys.exit(2)

    elif args.load:
        mode = "read"
    else:
        print("Call python3 aurror.py -h for help")


    model = "bin"
    election = {}
    election["ballots_cast"] = ballots_cast
    election["alpha"] = alpha
    election["candidates"] = candidates
    election["results"] = results
    election["winners"] = winners
    election["name"] = name
    election["model"] = model
    election["pstop"] = pstop_goal
    election["round_schedule"] = round_schedule
    #election["round_schedule_expected"] = map(round, (sum(results)/ballots_cast) * round_schedule)
    save_to = "elections/" + name




    tools.print_election(election)


    print("Round schedule: " + str(round_schedule))

    for i in range(len(candidates)):
        ballots_i = results[i]
        candidate_i = candidates[i]
        for j in range(i + 1, len(candidates)):
            ballots_j = results[j]
            candidate_j = candidates[j]

            print("\n\n%s (%s) vs %s (%s)" % (candidate_i, ballots_i, candidate_j, ballots_j))
            bc = ballots_i + ballots_j
            winner = max(ballots_i, ballots_j)
            print("\tmargin:\t" + str((winner - min(ballots_i, ballots_j))/bc))
            rs = []

            #print(str(round_schedule))
            for x in round_schedule:
                y = math.floor(x * bc / ballots_cast)
                rs.append(y)

            #print(str(rs))

            print("\n\tEffective round schedule: " + str(rs))

            margin = (2 * winner - bc)/bc

            audit_aurror = aurror(margin, alpha, rs)
            kmins = audit_aurror["kmins"]
            prob_sum = audit_aurror["prob_sum"]
            prob_tied_sum = audit_aurror["prob_tied_sum"]
            print("\tAurror kmins:\t" + str(kmins))
            print("\tAurror risk: \t" + str(prob_tied_sum))
            print("\tAurror pstop:\t" + str(prob_sum))

