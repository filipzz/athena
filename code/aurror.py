import sys
import argparse
import string
import math
import tools
from aurror.aurror import AurrorAudit

if (__name__ == '__main__'):

    info_text = 'This program lets for computing AURROR parameters.'
    parser = argparse.ArgumentParser(description=info_text)
    parser.add_argument("-v", "-V", "--version", help="shows program version", action="store_true")
    parser.add_argument("-n", "--new", help="creates new election folder where all data are stored")
    parser.add_argument("-a", "--alpha", help="set alpha (risk limit) for the election", type=float, default=0.1)
    parser.add_argument("-c", "--candidates", help="set the candidate list (names)", nargs="*")
    parser.add_argument("-b", "--ballots", help="set the list of ballots cast for every candidate", nargs="*", type=int)
    parser.add_argument("-t", "--total", help="set the total number of ballots in given contest", type=int)
    parser.add_argument("-r", "--rounds", "--round_schedule", help="set the round schedule", nargs="+", type=int)
    parser.add_argument("-p", "--pstop", help="set stopping probability goals for each round (corresponding round schedule will be found)", nargs="+", type=float)
    parser.add_argument("-w", "--winners", help="set number of winners for the given race", type=int, default=1)
    parser.add_argument("-l", "--load", help="set the election to read")
    parser.add_argument("--type", help="set the audit type (BRAVO/AURROR)", default="AURROR")
    parser.add_argument("-e", "--risk", "--evaluate_risk", help="evaluate risk for given audit results", nargs="+", type=int)
    args = parser.parse_args()

    audit_type = "AURROR"

    if args.version:
        print("AURROR version 0.3")
    if args.new:
        mode = "new"
        name = args.new

        alpha = args.alpha
        if alpha < 0.0 or alpha > 1.0:
            print("Value of alpha is incorrect")
            sys.exit(2)

        if args.type:
            if (args.type).lower() == "bravo" or (args.type).lower() == "wald":
                audit_type = "BRAVO"
            elif (args.type).lower() == "arlo":
                audit_type = "ARLO"

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
            print(str(pstop_goal))

        elif args.rounds:
            mode_rounds = "rounds"
            round_schedule = args.rounds
            pstop_goal = []
            if max(round_schedule) > ballots_cast:
                print("Round schedule is incorrect")
                sys.exit(2)
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
            eval_risk = "true"
            actual_kmins = args.risk

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
    save_to = "elections/" + name

    tools.print_election(election)

    print("Round schedule: " + str(round_schedule))

    if mode_rounds == "rounds":
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

                for x in round_schedule:
                    y = math.floor(x * bc / ballots_cast)
                    rs.append(y)

                margin = (2 * winner - bc)/bc

                audit_object = AurrorAudit()
                if audit_type.lower() == "bravo" or audit_type.lower() == "wald":
                    audit_aurror = audit_object.bravo(margin, alpha, rs)
                elif audit_type.lower() == "arlo":
                    audit_aurror = audit_object.arlo(margin, alpha, rs)
                else:
                    audit_aurror = audit_object.aurror(margin, alpha, rs)
                kmins = audit_aurror["kmins"]
                prob_sum = audit_aurror["prob_sum"]
                prob_tied_sum = audit_aurror["prob_tied_sum"]
                print("\n\tApprox round schedule:\t" + str(rs))
                print("\t%s kmins:\t\t%s" % (audit_type, str(kmins)))
                print("\t%s pstop (tied): \t%s" % (audit_type, str(prob_tied_sum)))
                print("\t%s pstop (audit):\t%s" % (audit_type, str(prob_sum)))

                true_risk = []
                for p, pt in zip(prob_sum, prob_tied_sum):
                    if p == 0:
                        true_risk.append(0.0)
                    else:
                        true_risk.append(pt/p)
                print("\t%s true risk:\t%s" % (audit_type, str(true_risk)))

    elif mode_rounds == "pstop":
        print("setting round schedule")
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
                for x in round_schedule:
                    y = math.floor(x * bc / ballots_cast)
                    rs.append(y)

                margin = (2 * winner - bc)/bc

                audit_object = AurrorAudit()

                print("pstop goal: " + str(pstop_goal))
                print("round schedule: " + str(rs))
                x = audit_object.find_next_round_sizes(margin, alpha, rs, pstop_goal)
