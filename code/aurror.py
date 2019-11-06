import json
import math
import os, sys, argparse

import schedule as schedule
import tools as tools

if (__name__ == '__main__'):

    info_text = 'This program lets for computing AURROR parameters.'
    parser = argparse.ArgumentParser(description=info_text)
    parser.add_argument("-v","-V", "--version", help="shows program version", action="store_true")
    parser.add_argument("-n", "--new", help="creates new election folder where all data are stored")
    parser.add_argument("-a", "--alpha", help="set alpha (risk limit) for the election", type=float)
    parser.add_argument("-t", "--total", help="set number of valid ballots cast", type=int)
    parser.add_argument("-c", "--candidates", help="set the candidate list (names)", nargs="*")
    parser.add_argument("-b", "--ballots", help="set the list of ballots cast for every candidate", nargs="*", type=int)
    parser.add_argument("-r", "-rs", "--rounds", "--round_schedule", help="set the round schedule", nargs="+", type=int)
    parser.add_argument("-w", "--winners", help="set number of winners for the given race", type=int, default=1)
    parser.add_argument("-e", "--election", help="set the election to read")
    args = parser.parse_args()

    if args.version:
        print("AURROR version 0.2")
    if args.new:
        mode = "new"
        name = args.new
        if args.alpha:
            alpha = args.alpha
            if alpha < 0.0 or alpha > 1.0:
                print("Value of alpha is inncorect")
                sys.exit(2)
        else:
            print("Missing -a / --alpha argument")
            sys.exit(2)

        # ballots
        if args.total:
            ballots_cast = args.total
        else:
            print("Missing -t / --total argument")
            sys.exit(2)

        if args.ballots:
            results = args.ballots
            if sum(results) != ballots_cast:
                print("Number of votes for candidates does not match with number of valid ballots cast")
                sys.exit(2)
        else:
            print("Missing -b / --ballots argument")
            sys.exit(2)

        if args.candidates:
            candidates = args.candidates
            if len(args.candidates) != len(args.ballots):
                print("Number of candidates does not match number of results")
                sys.exit(2)
        else:
            print("Missing -c / --candidates argument")
            sys.exit(2)

        if args.rounds:
            round_schedule = args.rounds
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

    elif args.election:
        mode = "read"
    else:
        print("Call python3 aurror.py -h for help")


    #     full_cmd_arguments = sys.argv
    #     argument_list = full_cmd_arguments[1:]
    #     unix_options = "n:e:ho:va:b:c:"
    #     gnu_options = ["new=", "election=", "help", "output=", "verbose", "alpha", "ballots", "candidates"]
    #
    #     try:
    #         arguments, values = getopt.getopt(argument_list, unix_options, gnu_options)
    #     except getopt.error as err:
    #         print(str(err))
    #         sys.exit(2)
    #
    #     for current_argument, current_value in arguments:
    #         if current_argument in ("-n", "--new"):
    #             mode = "new"
    #             name = current_value
    #         elif current_argument in ("-e", "--election"):
    #             mode = "election"
    #             name = current_value
    #         elif current_argument in ("-b", "--ballots"):
    #             ballots_cast = current_value
    #         elif current_argument in ("-a", "--alpha"):
    #             no_of_candidates = current_value
    #         elif

    model = "bin"
    election = {}
    election["ballots_cast"] = ballots_cast
    #election["margin"] = .1
    election["alpha"] = alpha
    #election["winner"] = math.floor((1+margin)*ballots_cast / 2)
    election["candidates"] = candidates
    election["results"] = results
    election["winners"] = winners
    election["name"] = name
    election["model"] = model
    election["round_schedule"] = round_schedule
    save_to = "elections/" + name



#    try:
#        os.mkdir(save_to)
#    except OSError:
#        sys.exit("Selected folder with election data already exists.")

#    with open(save_to + "/election.json", 'w') as f:
#        json.dump(election, f)


#    if len(sys.argv) < 5:
 #       print("python3 aurror.py ballots_cast winner margin [round_schedule]")

  #  if len(sys.argv) > 1:
   #     ballots_cast = int(sys.argv[1])

   # print(ballots_cast)


    tools.print_election(election)

    #round_schedule = [100, 200, 400]

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
            rs = []
            for x in round_schedule:
                y = math.floor(x * bc / ballots_cast)
                rs.append(y)

            print("\tEffective round schedule: " + str(rs))
            # Calling: find_aurror_params_from_schedule(...)
            # 1. finds parameters for BRAVO
            # 2. finds parameters for Aurror
            schedule.find_aurror_params_from_schedule(bc, winner, alpha, model, rs, "false")
            # for one-round better results are acheived by:
            #schedule.find_aurror_params_from_schedule_and_risk(bc, winner, alpha, model, rs, [alpha])
