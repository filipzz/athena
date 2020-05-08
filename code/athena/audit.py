import logging
import math
import sys

from .athena import AthenaAudit
from .election import Election

class Audit():

    def __init__(self, audit_type, alpha = 0.1, delta = 1):
        self.audit_type = audit_type
        self.election = Election()
        self.round_schedule = []
        self.audit_observations = [[]]
        self.round_observations = [[]]
        self.audit_kmins = []
        self.alpha = alpha
        self.delta = delta
        self.election_data_file = ""




    def add_election(self, election):
        new_election = Election(election)
        self.election = new_election
        #self.audit_observations = [[0 for i in range(1)] for j in range(len(self.election.candidates))]
        self.audit_observations = [[] for j in range(len(self.election.candidates))]
        self.round_observations = [[] for j in range(len(self.election.candidates))]
        #for i in range(len(self.election.candidates)):
        #    self.audit_observations[i].append([])

    def read_election_results(self, url):
        self.election_data_file = url
        self.election.read_election_data(url)

    def load_contest(self, contest):
        self.election.load_contest_data(contest)
        self.audit_observations = [[] for j in range(len(self.election.candidates))]
        self.round_observations = [[] for j in range(len(self.election.candidates))]

    def get_contests(self):
        contest_list = []
        for contest in self.election.data:
            if contest not in {'total_ballots', 'd_ballots', 'r_ballots', 'nonpartisan_ballots'}:
                contest_list.append(contest)

        return contest_list


    def add_round_schedule(self, round_schedule):
        self.round_schedule = round_schedule


    # deprecated - we need to know the sample size anyway
    def extend_round_schedule(self, next_round):
        logging.info("Current round schedule:\t%s" % (self.election.round_schedule))
        self.round_schedule.append(next_round)
        logging.info("New round schedule:\t%s" % (self.election.round_schedule))
        logging.info("Extended observations")
        for i in range(self.election.candidates):
            self.audit_observations[i].append([0])
        logging.info(self.audit_observations)

    def add_observations(self, observations):
        logging.info("Updating round schedule")
        new_valid_ballots = sum(observations)
        if len(self.round_schedule) > 0:
            self.round_schedule = self.round_schedule + [new_valid_ballots + max(self.round_schedule)]
            #actual_kmins = actual_kmins + [new_winner + max(actual_kmins)]
        else:
            self.round_schedule = [new_valid_ballots]
            #actual_kmins = [new_winner]
        logging.info(self.round_schedule)

        logging.info("Current observations: " + str(self.audit_observations))
        for i in range(len(self.election.candidates)):
            #print(self.audit_observations)
            #print(observations[i])
            self.round_observations[i].append(observations[i])
            if len(self.audit_observations[i]) > 0:
                self.audit_observations[i].append(max(self.audit_observations[i]) + observations[i])
            else:
                self.audit_observations[i].append(observations[i])

        #print(self.round_observations)
        #print(self.audit_observations)

    def find_next_round_size(self, pstop_goals):
        logging.info("setting round schedule")

        found_solutions = {}
        future_round_sizes = [0] * len(pstop_goals)
        #future_prob_stop = [0] * len(pstop_goals)

        #for i in range(len(self.election.candidates)):
        for i in self.election.declared_winners:
            ballots_i = self.election.results[i]
            candidate_i = self.election.candidates[i]
            #for j in range(i + 1, len(self.election.candidates)):
            for j in self.election.declared_losers:
                ballots_j = self.election.results[j]
                candidate_j = self.election.candidates[j]

                logging.info("\n\n%s (%s) vs %s (%s)" % (candidate_i, (ballots_i), candidate_j, (ballots_j)))
                bc = ballots_i + ballots_j
                scalling_ratio = self.election.ballots_cast / bc

                winner = max(ballots_i, ballots_j)
                logging.info("\tmargin:\t" + str((winner - min(ballots_i, ballots_j))/bc))
                rs = []
                #for x in self.round_schedule:
                #    y = math.floor(x * bc / self.election.ballots_cast)
                #    rs.append(y)
                for rs_i, rs_j in zip(self.audit_observations[i], self.audit_observations[j]):
                    rs.append(rs_i + rs_j)


                margin = (2 * winner - bc)/bc

                audit_object = AthenaAudit()

                #logging.info("\tpstop goals: " + str(pstop_goals))
                logging.info("\tpairwise round schedule: " + str(rs))
                rescaled = []
                next_round_sizes = audit_object.find_next_round_sizes(self.audit_type, margin, self.alpha, self.delta,
                                                                      rs, pstop_goals)
                for i, pstop_goal, next_round, prob_stop in zip(range(len(pstop_goals)), pstop_goals, next_round_sizes["rounds"], next_round_sizes["prob_stop"]):
                    rs = [] + self.round_schedule
                    next_round_rescaled = math.ceil(next_round * scalling_ratio)
                    rs.append(next_round_rescaled)
                    rescaled.append(next_round_rescaled)
                    future_round_sizes[i] = max(future_round_sizes[i], next_round_rescaled)
                    logging.info("\t\t%s:\t%s\t%s" % (pstop_goal, rs, prob_stop))
                    logging.info("\t\t\t\tnr: %s\trnr: %s\tsr: %s" % (next_round, next_round_rescaled, scalling_ratio))

                found_solutions[candidate_i + "-" + candidate_j] = {"pstop_goal": pstop_goals, "next_round_sizes": rescaled, "prob_stop": next_round_sizes["prob_stop"]}

        return {"detailed" : found_solutions, "future_round_sizes" : future_round_sizes}

    def find_risk(self):#, audit_observations):
        result = {}

        test_passed = True
        passed = 0
        risks = []
        delta =[]
        smallest_margin = 1
        smallest_margin_id = ""

        #for i in range(len(self.election.candidates)):
        for i in self.election.declared_winners:
            ballots_i = self.election.results[i]
            candidate_i = self.election.candidates[i]
            #for j in range(i + 1, len(self.election.candidates)):
            for j in self.election.declared_losers:
                pair_id = str(i) + "-" + str(j)
                ballots_j = self.election.results[j]
                candidate_j = self.election.candidates[j]

                logging.info("\n\n%s (%s) vs %s (%s)" % (candidate_i, (ballots_i), candidate_j, (ballots_j)))
                bc = ballots_i + ballots_j
                winner = max(ballots_i, ballots_j)
                if winner == ballots_i:
                    winner_pos = i
                    loser_pos = j
                else:
                    winner_pos = j
                    loser_pos = i
                logging.info("\tmargin:\t" + str((winner - min(ballots_i, ballots_j))/bc))
                rs = []

                #for x in self.round_schedule:
                #    y = math.floor(x * bc / self.election.ballots_cast)
                #    rs.append(y)

                # we build a round schedule that takes into account only relevant ballots for the given pair
                for rs_i, rs_j in zip(self.audit_observations[i], self.audit_observations[j]):
                    rs.append(rs_i + rs_j)

                #print("round schedule", rs)

                margin = (2 * winner - bc)/bc

                audit_object = AthenaAudit()
                if self.audit_type.lower() == "bravo" or self.audit_type.lower() == "wald":
                    audit_athena = audit_object.bravo(margin, self.alpha, rs)
                elif self.audit_type.lower() == "arlo":
                    audit_athena = audit_object.arlo(margin, self.alpha, rs)
                elif self.audit_type.lower() == "minerva":
                    audit_athena = audit_object.minerva(margin, self.alpha, rs)
                elif self.audit_type.lower() == "metis":
                    audit_athena = audit_object.metis(margin, self.alpha, rs)
                else:
                    audit_athena = audit_object.athena(margin, self.alpha, self.delta, rs)

                #risk_goal = audit_athena["prob_tied_sum"]
                pairwise_audit_kmins = []
                #self.audit_kmins = audit_athena["kmins"]
                pairwise_audit_kmins = audit_athena["kmins"]

                logging.info(str(audit_athena))

                #test_info = audit_object.find_kmins_for_risk(self.audit_kmins, self.audit_observations[winner_pos])
                test_info = audit_object.find_kmins_for_risk(pairwise_audit_kmins, self.audit_observations[winner_pos])

                logging.info("find_kmins_for_risk")
                logging.info(str(test_info))

                logging.info("\n\t\tAUDIT result for: " +  str(candidate_i) + " vs " + str(candidate_j))
                logging.info("\t\trequired winner:\t" + str(pairwise_audit_kmins))
                logging.info("\t\tobserved winner:\t" + str(self.audit_observations[winner_pos]))
                logging.info("\t\tobserved loser: \t" + str(self.audit_observations[loser_pos]))
                logging.info("\t\tround schedule: \t" + str(rs))

                if test_info["passed"] == 1:
                    logging.info("\n\t\tTest passed")
                else:
                    logging.info("\n\t\tTest FAILED")

                #w = audit_object.estimate_risk(margin, actual_kmins, round_schedule)
                #w = audit_object.estimate_risk(margin, test_info["kmins"], self.round_schedule, audit_observations)
                #w = audit_object.estimate_risk(margin, self.audit_kmins, self.round_schedule, audit_observations)
                w = audit_object.estimate_risk(margin, pairwise_audit_kmins, rs, self.audit_observations[winner_pos])
                #logging.info(str(w))
                #ratio = w["ratio"]
                deltas = w["deltas"]
                audit_risk = min(filter(lambda x: x > 0, w["audit_ratio"]))
                #logging.info(str(w))
                #logging.info("Risk spent:\t%s" % (ratio[-1]))
                logging.info("\t\tLR [needs to be > %s]:\t\t\t%s" % (self.delta, 1/deltas[-1]))
                logging.info("\t\tATHENA risk [needs to be <= %s]:\t%s" % (self.alpha, audit_risk))

                if test_info["passed"] != 1:
                    test_passed = False

                risks.append(audit_risk)
                delta.append(deltas[-1])

                result[pair_id] = {"risk": audit_risk, "delta": deltas[-1],  "passed": test_info["passed"], "observed_winner": self.audit_observations[winner_pos], "observed_loser": self.audit_observations[loser_pos], "required": pairwise_audit_kmins}

                if margin < smallest_margin:
                    smallest_margin = margin
                    smallest_margin_id = pair_id


        if test_passed == True:
            passed = 1

        return {"risk": max(risks), "delta": min(delta), "passed": passed, "observed": result[smallest_margin_id], "required": result[smallest_margin_id], "pairwise": result}


    def run_interactive(self):
        round_number = 1
        audit_completed = False
        list_of_candidates = self.election.candidates

        while audit_completed is False:
            print("\n\n---------------------- Round number: ", round_number, " -----------------\n")
            print("Your choices: ")
            print("[1] Find next round size at 70%, 80%, 90%")
            print("[2] Enter other goal for probability of stopping.")
            choice = input("Enter your choice: ")
            if choice == "1":
                pstop_goal = [.7, .8, .9]
            elif choice == "2":
                pstop_choice = float(input("Enter value: "))
                if 0 < pstop_choice < 1:
                    pstop_goal = [pstop_choice]
                elif 1 <= pstop_choice <= 99:
                    pstop_goal = [pstop_choice/100]
                else:
                    print("Entered value is incorrect")
                    sys.exit(1)
            else:
                audit_completed = True

            x = self.find_next_round_size(pstop_goal)
            #print(str(x))

            future_round_sizes = x["future_round_sizes"]

            if len(self.round_schedule) > 0:
                below_kmin = 0 #max(required) - max(observed)
                n_future_round_sizes =  list(map(lambda x: x - max(self.round_schedule) + 2 * below_kmin, future_round_sizes))
            else:
                n_future_round_sizes = future_round_sizes

            print("\nSelect round size: ")
            for p, rs in zip(pstop_goal, n_future_round_sizes):
                print("Complete with prob. %s when you sample %s more ballots." % (p, rs))


            ###del w

            correct_valid_total = False
            correct_candidates_total = False

            while correct_valid_total is False:
                #print("\n\nEnter the number of ballots drawn in this round: ")
                message = "\n\n\tEnter the number of (all) ballots drawn in this round: " # + str(round_number) + ": "
                new_ballots = int(input(message))
                new_valid_ballots = new_ballots

                #print("\n\n\tEnter the number of relevant ballots: ")
                new_valid_ballots = int(input("\tEnter the number of relevant ballots: "))

                if new_valid_ballots <= new_ballots:
                    correct_valid_total = True
                else:
                    print("Incorrect number of valid ballots entered: ", new_valid_ballots, " > ", new_ballots)



            while correct_candidates_total is False:
                print("\n\tEnter number of ballots for each candidate:")
                round_observation = []
                vote_in_round = 0
                for i in range(len(list_of_candidates)):
                    message = "\tBallots for " + list_of_candidates[i] + ": "
                    candidate_votes = int(input(message))
                    vote_in_round = vote_in_round + candidate_votes
                    round_observation.append(candidate_votes)

                if vote_in_round == new_valid_ballots:
                    correct_candidates_total = True
                else:
                    print("\nSum of votes for candidates does not match the number of valid ballots.")



            #if len(round_schedule) > 0:
            #    round_schedule = round_schedule + [new_valid_ballots + max(round_schedule)]
            #    #actual_kmins = actual_kmins + [new_winner + max(actual_kmins)]
            #else:
            #    round_schedule = [new_valid_ballots]
            #    #actual_kmins = [new_winner]


            ###w = Audit(audit_type, alpha, delta)
            ###w.add_election(election)
            #w.add_round_schedule(round_schedule)
            #w.audit_observations(round_observation)
            #w.add_observations(new_valid_ballots, round_observation)
            self.add_observations(round_observation)
            round_schedule = self.round_schedule
            #print("round_schedule", round_schedule)
            x = self.find_risk() #actual_kmins)
            observed = x["observed"]
            required = x["required"]

            if x["passed"] == 1:
                audit_completed = True
                print("\n\n\tAudit Successfully completed!")
                print("\tP-value:\t%s\n" % (x["risk"]))
                #print(x)
            else:
                print("\n\nAudit failed")
                print("\tLR:\t\t%s\t[needs to be > %s]" % (1/x["delta"], self.delta))
                print("\tATHENA risk:\t%s\t[needs to be <= %s]" % (x["risk"], self.alpha))
                print("\tboth conditions are required to be satisfied.")
                #print("P-value:\t%s\n" % (x["risk"]))

            round_number = round_number + 1
            #print(str(x))
            ###del w

