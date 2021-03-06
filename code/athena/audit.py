import logging
import math
import sys

from .athena import AthenaAudit
from .election import Election


class Status:
    def __init__(self):
        self.round_number = 1
        self.params = []
        self.min_kmins = []
        self.risks = []
        self.deltas = []
        self.audit_pairs = []
        self.audit_completed = False
        self.ballots_sampled = []
        self.observations = []
        self.rs = []
        self.pairwise = []
        self.results = []

    def get_status(self):
        return self.audit_completed

    def get_pairwise(self):
        return self.pairwise

    def get_pval(self):
        return self.risks[-1]

    def __repr__(self):
        return f"""{{"audit_passed": {self.audit_completed}, 
            "min_kmins": {self.min_kmins}, 
            "risks": {self.risks}, 
            "rs": {self.rs},
            "audit_pairs": {self.audit_pairs},
            "observations": {self.observations},
            "pairwise": {self.pairwise},
            "round_number": {self.round_number}}}"""


class Audit:

    def __init__(self, audit_type, alpha = 0.1, delta = 1):
        self.election = Election()
        self.active_contest = None
        self.observations = {}
        self.audit_observations = []
        self.status = {}
        self.audit_type = audit_type
        #self.election = Contest()
        self.audited_contests = []
        self.round_schedule = []
        self.alpha = alpha
        self.delta = delta
        self.election_data_file = ""
        self.ballots_cast = 0
        self.data = None
        self.contests = []
        self.contest_list = []
        self.data_frame = {}
        self.convolve_method = 'direct'
        self.approximation_threshold = 0.015

    def __repr__(self):
        return f'audit type: {self.audit_type}\n' \
               f'alpha: {self.alpha}\n' \
               f'round_schedule: {self.round_schedule}\n' \
               f'observations: {self.observations}\n' \
               f'status: {self.status!r}'

    """Sets convolve method to: method"""
    def set_colvolve_method(self, method):
        self.convolve_method = method

    """Sets approximation threshold to: threshold (to speed up finding round sizes)"""
    def set_approximation_threshold(self, threshold):
        if 0 < threshold < 1:
            self.approximation_threshold = threshold

    def get_status(self, contest_name):
        return self.status[contest_name].get_status()

    def get_pval(self, contest_name):
        return self.status[contest_name].get_pval()

    def read_election_results(self, url):
        self.election_data_file = url
        election_data = self.election.read_election_data(url)
        self.add_election(election_data)

    def add_election(self, election):
        new_election = Election(election) # Contest(election["data"])
        self.election = new_election
        self.ballots_cast = self.election.total_ballots # temporary

        first_contest = True
        for contest_name in self.election.contests:
            self.contest_list.append(contest_name)
            self.observations[contest_name] = [[] for j in range(self.election.contests[contest_name].num_candidates)]
            self.status[contest_name] = Status()
            if first_contest is True:
                self.active_contest = contest_name
                first_contest = False

    def add_contest(self, contest_dict):
        total_ballots = sum(tally for tally in contest_dict['tally'].values())
        election_name = "election_name"
        contest_name = "contest_name"
        election = {
            'name': election_name,
            'total_ballots': total_ballots,
            'contests': {contest_name: contest_dict}
        }
        self.add_election(election)
        self.active_contest = contest_name

    def get_contests(self):
        x = self.data["contests"]
        y = x.keys()
        return list(y)

        #return list(self.data["contests"].keys())

    def load_contest(self, contest_name):
        self.active_contest = contest_name
        self.audit_observations = self.observations[contest_name] # to be removed

        self.status[contest_name].audit_pairs = []

        #print(str(self.election.contests[contest_name].declared_winners))
        #print(str(self.election.contests[contest_name].declared_losers))
        for winner in self.election.contests[contest_name].declared_winners:
            for loser in self.election.contests[contest_name].declared_losers:
                #print("[%s, %s]" % (winner, loser))
                self.status[contest_name].audit_pairs.append([winner, loser])

        #print(str(self.status[contest_name].audit_pairs))
        #print(str(self.election.contests[contest_name].au))

    def add_round_schedule(self, round_schedule):
        self.round_schedule = round_schedule


    def add_observations(self, observations, contest_name = None):

        if contest_name is None:
            contest_name = self.active_contest

        new_valid_ballots = sum(observations)
        if len(self.round_schedule) > 0:
            self.round_schedule = self.round_schedule + [new_valid_ballots + max(self.round_schedule)]
        else:
            self.round_schedule = [new_valid_ballots]

        for i in range(len(self.election.contests[contest_name].candidates)):
            if len(self.observations[contest_name][i]) > 0:
                self.observations[contest_name][i].append(max(self.observations[contest_name][i]) + observations[i])
            else:
                self.observations[contest_name][i].append(observations[i])

    """
    Method that simulates a single round of the audit
    """
    def set_observations(self, new_ballots, new_valid_ballots, round_observation, contest_name = None):
        """
        Parameters
        ----------
        :param new_ballots: number of total ballots sampled in the round
        :param new_valid_ballots: number of ballots sampled in the round that are relevant to the contest
        :param round_observation: an array of number of ballots sampled for each candidate in the round
        :param contest_name: a name of a contest for which audit observations are added
        """

        if contest_name is None:
            contest_name = self.active_contest

        if self.status[contest_name].audit_completed:
            raise ValueError("Audit already completed")
        else:

            votes_allowed = self.election.contests[contest_name].votes_allowed

            #if new_valid_ballots > votes_allowed * new_ballots or \
            if sum(round_observation) > votes_allowed * new_valid_ballots:
                raise ValueError("Incorrect number of valid ballots entered")

            self.add_observations(round_observation, contest_name)
            x = self.find_risk() #actual_kmins)
            #observed = x["observed"]
            #required = x["required"]
            #print("asd: " + str(x))
            self.status[contest_name].min_kmins = x["min_kmins"]
            self.status[contest_name].risks.append(x["risk"])
            self.status[contest_name].deltas.append(x["delta"])
            self.status[contest_name].ballots_sampled.append(new_valid_ballots)
            self.status[contest_name].pairwise.append(x["pairwise"])

            if x["passed"] == 1:
                self.status[contest_name].audit_completed = True
                logging.info("\n\n\tAudit Successfully completed!")
                #logging.info("\tLR:\t\t%s\t[needs to be > %s]" % (1/x["delta"], self.delta))
                #logging.info("\tDelta:\t\t%s\t[needs to be < %s]" % (x["delta"], self.delta))
                logging.info("\tp-value:\t%s\t[needs to be <= %s]" % (x["risk"], self.alpha))
            else:
                logging.info("\n\n\tRound: %s audit failed" % (self.status[contest_name].round_number))
                #logging.info("\tLR:\t\t%s\t[needs to be > %s]" % (1/x["delta"], self.delta))
                #logging.info("\tDelta:\t\t%s\t[needs to be < %s]" % (x["delta"], self.delta))
                logging.info("\tp-value:\t%s\t[needs to be <= %s]" % (x["risk"], self.alpha))
                #logging.info("\tboth conditions are required to be satisfied.")

            self.status[contest_name].round_number = self.status[contest_name].round_number + 1
            self.status[contest_name].params.append(x)

    def find_next_round_size(self, pstop_goals, contest_name = None):
        if contest_name is None:
            contest_name = self.active_contest
        logging.info("setting round schedule")
        found_solutions = {}
        future_round_sizes = [0] * len(pstop_goals)
        #future_prob_stop = [0] * len(pstop_goals)

        #print("audit pairs: %s" % (self.status[contest_name].audit_pairs))

        for i, j in self.status[contest_name].audit_pairs:
            #for i in self.election.declared_winners:
            ballots_i = self.election.contests[contest_name].results[i]
            candidate_i = self.election.contests[contest_name].candidates[i]
            #for j in self.election.declared_losers:
            ballots_j = self.election.contests[contest_name].results[j]
            candidate_j = self.election.contests[contest_name].candidates[j]

            if len(self.observations[contest_name][i]) > 0:
                #observations in the last round:
                observations_i = self.observations[contest_name][i][-1]
                #print("i -> " + str(observations_i))
                observations_j = self.observations[contest_name][j][-1]
                #print("j -> " + str(observations_j))
            else:
                observations_i = 0
                observations_j = 0

            logging.info("\n\n%s (%s) vs %s (%s)" % (candidate_i, (ballots_i), candidate_j, (ballots_j)))
            bc = ballots_i + ballots_j
            scalling_ratio = self.election.total_ballots / bc

            winner = max(ballots_i, ballots_j)
            logging.info("\tmargin:\t" + str((winner - min(ballots_i, ballots_j))/bc))
            rs = []
            #for x in self.round_schedule:
            #    y = math.floor(x * bc / self.election.ballots_cast)
            #    rs.append(y)
            for rs_i, rs_j in zip(self.audit_observations[i], self.audit_observations[j]):
                #print("%s %s" % (rs_i, rs_j))
                rs.append(rs_i + rs_j)


            margin = (2 * winner - bc)/bc

            audit_object = AthenaAudit(self.audit_type, self.alpha, self.delta)
            audit_object.set_convolve_method(self.convolve_method)
            audit_object.set_approximation_threshold(self.approximation_threshold)
            #print("---------" + str(rs))
            #audit_object.audit(margin, rs)

            #logging.info("\tpstop goals: " + str(pstop_goals))
            logging.info("\tpairwise round schedule: " + str(rs))
            rescaled = []
            next_round_sizes = audit_object.find_next_round_sizes(margin, rs,
                                                                  pstop_goals, observations_i)
            for k, pstop_goal, next_round, prob_stop in zip(range(len(pstop_goals)), pstop_goals, next_round_sizes["rounds"], next_round_sizes["prob_stop"]):
                rs = [] + self.round_schedule
                next_round_rescaled = math.ceil(next_round * scalling_ratio)
                rs.append(next_round_rescaled)
                rescaled.append(next_round_rescaled)
                future_round_sizes[k] = max(future_round_sizes[k], next_round_rescaled)
                logging.info("\t\t%s:\t%s\t%s" % (pstop_goal, rs, prob_stop))
                logging.info("\t\t\t\tnr: %s\trnr: %s\tsr: %s" % (next_round, next_round_rescaled, scalling_ratio))

            found_solutions[candidate_i + "-" + candidate_j] = {"pstop_goal": pstop_goals, "next_round_sizes": rescaled, "prob_stop": next_round_sizes["prob_stop"]}

        return {"detailed" : found_solutions, "future_round_sizes" : future_round_sizes}


    def find_risk(self, contest_name = None):#, audit_observations):

        if contest_name is None:
            contest_name = self.active_contest

        result = {}

        test_passed = True
        passed = 0
        risks = []
        delta =[]
        smallest_margin = 1
        smallest_margin_id = ""
        #TODO: this approach works only for 2 candiates:
        min_kmins = [0] * len(self.election.contests[contest_name].candidates)

        audit_pairs_next = []
        for i, j in self.status[contest_name].audit_pairs:
        #for i in self.election.declared_winners:
            ballots_i = self.election.contests[contest_name].results[i] # TODO: change to tally
            candidate_i = self.election.contests[contest_name].candidates[i]
            #for j in range(i + 1, len(self.election.candidates)):
            #for j in self.election.declared_losers:
            pair_id = str(i) + "-" + str(j)
            ballots_j = self.election.contests[contest_name].results[j]
            candidate_j = self.election.contests[contest_name].candidates[j]

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
            #for rs_i, rs_j in zip(self.audit_observations[i], self.audit_observations[j]):
            for rs_i, rs_j in zip(self.observations[contest_name][i], self.observations[contest_name][j]):
                rs.append(rs_i + rs_j)

            margin = (2 * winner - bc)/bc

            audit_object = AthenaAudit(self.audit_type.lower(), self.alpha, self.delta)
            audit_object.set_convolve_method(self.convolve_method)
            audit_object.set_approximation_threshold(self.approximation_threshold)
            #TODO: check this call

            audit_athena = audit_object.audit(margin, rs)

            #risk_goal = audit_athena["prob_tied_sum"]
            pairwise_audit_kmins = []
            #self.audit_kmins = audit_athena["kmins"]
            pairwise_audit_kmins = audit_athena["kmins"]

            #print(str(audit_object.prob_distribution_margin))
            #print(str(audit_object.prob_distribution_tied))

            logging.info(str(audit_athena))

            #test_info = audit_object.find_kmins_for_risk(self.audit_kmins, self.audit_observations[winner_pos])
            #test_info = audit_object.find_kmins_for_risk(pairwise_audit_kmins, self.audit_observations[winner_pos])
            test_info = audit_object.find_kmins_for_risk(pairwise_audit_kmins, self.observations[contest_name][winner_pos])

            #print(str(test_info))
            logging.info("find_kmins_for_risk")
            logging.info(str(test_info))

            logging.info("\n\t\tAUDIT result for: " +  str(candidate_i) + " vs " + str(candidate_j))
            logging.info("\t\trequired winner:\t" + str(pairwise_audit_kmins))
            if pairwise_audit_kmins[-1] > min_kmins[winner_pos]:
                min_kmins[winner_pos] = pairwise_audit_kmins[-1]
            #logging.info("\t\tobserved winner:\t" + str(self.audit_observations[winner_pos]))
            #logging.info("\t\tobserved loser: \t" + str(self.audit_observations[loser_pos]))
            logging.info("\t\tobserved winner:\t" + str(self.observations[contest_name][winner_pos]))
            logging.info("\t\tobserved loser: \t" + str(self.observations[contest_name][loser_pos]))
            logging.info("\t\tround schedule: \t" + str(rs))

            if test_info["passed"] == 1:
                logging.info("\n\t\tTest passed")
            else:
                logging.info("\n\t\tTest FAILED")
                audit_pairs_next.append([i, j])

            #w = audit_object.estimate_risk(margin, actual_kmins, round_schedule)
            #w = audit_object.estimate_risk(margin, test_info["kmins"], self.round_schedule, audit_observations)
            #w = audit_object.estimate_risk(margin, self.audit_kmins, self.round_schedule, audit_observations)
            #w = audit_object.estimate_risk(margin, pairwise_audit_kmins, rs, self.audit_observations[winner_pos])
            #print("pairwise kmins: " + str(pairwise_audit_kmins))
            w = audit_object.estimate_risk(margin, pairwise_audit_kmins, rs, self.observations[contest_name][winner_pos])
            #logging.info(str(w))
            #ratio = w["ratio"]
            deltas = w["deltas"]
            #audit_risk = min(filter(lambda x: x > 0, w["audit_ratio"]))
            logging.debug("w: %s" % (w))
            audit_risk = w["audit_ratio"][-1]
            #logging.info(str(w))
            #logging.info("Risk spent:\t%s" % (ratio[-1]))
            if self.audit_type.lower in {"bravo", "athena", "arlo"}:
                if deltas[-1] > 0:
                    logging.info("\t\tdelta [needs to be > %s]:\t\t\t%s" % (self.delta, 1/deltas[-1]))
                else:
                    logging.info("\t\tdelta [needs to be > %s]:\t\t\tinf." % (self.delta))
                logging.info("\t\tLR [needs to be < %s]:\t\t%s" % (self.delta, deltas[-1]))
            logging.info("\t\tp-value [needs to be <= %s]:\t%s" % (self.alpha, audit_risk))

            if test_info["passed"] != 1:
                test_passed = False

            risks.append(audit_risk)
            delta.append(deltas[-1])

            result[pair_id] = {"risk": audit_risk, "delta": deltas[-1],  "passed": test_info["passed"],
                               "observed_winner": self.observations[contest_name][winner_pos],
                               "observed_loser": self.observations[contest_name][loser_pos],
                               "required": pairwise_audit_kmins,
                               "winner": self.election.contests[contest_name].candidates[winner_pos],
                               "loser": self.election.contests[contest_name].candidates[loser_pos]
                            }

            if margin < smallest_margin:
                smallest_margin = margin
                smallest_margin_id = pair_id


        if test_passed == True:
            passed = 1

        self.status[contest_name].results.append(result)

        self.status[contest_name].audit_pairs = audit_pairs_next

        logging.debug("risks: %s" % (risks))
        #logging.debug("delta: %s" % (delta))

        return {"risk": max(risks),
                "delta": max(delta),
                "deltamin": min(delta),
                "passed": passed,
                "observed": result[smallest_margin_id],
                "required": result[smallest_margin_id],
                "pairwise": result,
                "min_kmins": min_kmins
                }


    def run_interactive(self, contest_name = None):

        if contest_name is None:
            contest_name = self.active_contest

        while self.status[contest_name].audit_completed is False:
            self.run_audit_round(contest_name = None)


    def predict_round_sizes(self, pstop_goal):

        x = self.find_next_round_size(pstop_goal)

        future_round_sizes = x["future_round_sizes"]

        n_future_round_sizes = future_round_sizes

        predicted = []
        for p, s in zip(pstop_goal, n_future_round_sizes):
            predicted.append([p, s])


        return predicted

    def run_audit_round(self, contest_name = None):

        if contest_name is None:
            contest_name = self.active_contest

        if self.status[contest_name].audit_completed is True:
            logging.error("Audit is completed!")
            raise ValueError("Audit is completed")

        #round_number = 1
        #self.audit_completed = False
        list_of_candidates = self.election.contests[contest_name].candidates

        #while audit_completed is False:
        print("\n\n---------------------- Round number: ", self.status[contest_name].round_number, " -----------------\n")
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
            self.status[contest_name].audit_completed = True

        print(str(pstop_goal))
        predicted_round_sizes = self.predict_round_sizes(pstop_goal)

        logging.debug("predicted round size: %s" % (predicted_round_sizes))

        print("\nSelect round size: ")
        #print(str(predicted_round_sizes))
        #print(str(self.status))

        for prs in predicted_round_sizes:
            p, rs = prs
            print("Complete with prob. %s for the total number of ballots: %s." % (p, rs))


        ###del w

        correct_valid_total = False
        correct_candidates_total = False

        while correct_valid_total is False:
            #print("\n\nEnter the number of ballots drawn in this round: ")
            message = "\n\n\tEnter the number of (all) ballots drawn in this round: " # + str(round_number) + ": "
            new_ballots = int(input(message))

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
        self.status[contest_name].min_kmins = x["min_kmins"]
        self.status[contest_name].risks.append(x["risk"])
        self.status[contest_name].deltas.append(x["delta"])
        self.status[contest_name].ballots_sampled.append(new_valid_ballots)
        self.status[contest_name].observations.append(round_observation)
        self.status[contest_name].rs.append(sum(round_observation))

        if x["passed"] == 1:
            self.status[contest_name].audit_completed = True
            print("\n\n\tRound: %s audit completed" % (self.status[contest_name].round_number))
            #print("\tAudit Successfully completed!")
            print("\tP-value:\t%s\n" % (x["risk"]))
            self.status[contest_name].audit_completed = True
            #print(x)
        else:
            print("\n\n\tRound: %s audit failed" % (self.status[contest_name].round_number))
            #print("\tAudit failed")
            #print("\tDelta:\t\t%s\t[needs to be < %s]" % (1/x["delta"], self.delta))
            if self.audit_type.lower in {"arlo", "bravo", "athena"}:
                print("\tLR:\t\t%s\t[needs to be > %s]" % (x["delta"], self.delta))
            #print("\tDelta:\t\t%s\t[needs to be < %s]" % (1/x["delta"], self.delta))
            print("\tP-value:\t%s\t[needs to be <= %s]" % (x["risk"], self.alpha))
            #print("\tboth conditions are required to be satisfied.")
            #print("P-value:\t%s\n" % (x["risk"]))

            #round_number = round_number + 1
            #print(str(x))
            ###del w
        self.status[contest_name].round_number = self.status[contest_name].round_number + 1

    def show_election_results(self, contest_name = None):
        import pandas as pd

        if contest_name is None:
            contest_name = self.active_contest
        #d = {'Candidates': self.election.candidates, 'Results': self.election.results}
        d = {'Candidates': self.election.contests[contest_name].candidates,
             'Results': self.election.contests[contest_name].results}
        df = pd.DataFrame(data=d)
        return df.style.set_properties(subset = pd.IndexSlice[self.election.contests[contest_name].winners, :], **{'color' : 'green'})


    '''
    Method presents a DataFrame with audit results
    '''
    def present_state(self, contest_name = None):
        import pandas as pd

        if contest_name is None:
            contest_name = self.active_contest

        if self.status[contest_name].round_number == 0:
            return self.show_election_results()

        summary = ["Sum", "LR", "P-Value"]

        '# columns related to election results'
        list_of_candidates = [] + self.election.contests[contest_name].candidates
        for a in summary:
            list_of_candidates.append(" ") # this is sum row
        #list_of_candidates.append(" ") # this is delta row
        #list_of_candidates.append(" ") # this is p-value row

        audit_results = [] + self.election.contests[contest_name].results
        for a in summary:
            audit_results.append(a)

        d = {'Candidates': list_of_candidates, 'Results': audit_results}
        df = pd.DataFrame(data=d)

        '# columns related to audit rounds'
        if self.status[contest_name].round_number > 1:

            '# Results column of results of sampling'
            for rd in range(self.status[contest_name].round_number - 1):
                col_caption = "Round " + str(rd + 1)
                r = []
                for i in range(len(self.election.contests[contest_name].candidates)):
                    #r.append(self.audit_observations[i][rd])
                    if rd > 0:
                        r.append((self.observations[contest_name][i][rd] - self.observations[contest_name][i][rd-1]))
                    else:
                        r.append(self.observations[contest_name][i][rd])
                r.append(str(self.status[contest_name].ballots_sampled[rd]))
                #r.append("{:.4f}".format(1/self.status[contest_name].deltas[rd]))
                r.append(" ")
                r.append("{:.4f}".format(self.status[contest_name].risks[rd]))
                df[col_caption] = r

            '# Total column - sum of sampled ballots'
            r = []
            col_caption = "Total"
            for i in range(len(self.election.contests[contest_name].candidates)):
                #r.append(self.audit_observations[i][self.status[contest_name].round_number - 2])
                r.append(self.observations[contest_name][i][self.status[contest_name].round_number - 2])
            for i in summary:
                r.append(" ")
            df[col_caption] = r

            '# Column Required - presents the value of kmin required to pass the audit'
            r = []
            col_caption = "Required"
            for i in range(len(self.election.contests[contest_name].candidates)):
                if self.status[contest_name].min_kmins[i] == 0:
                    r.append(" ")
                else:
                    r.append(self.status[contest_name].min_kmins[i])
            for i in summary:
                r.append(" ")
            df[col_caption] = r

        #return df.style.set_properties(subset = pd.IndexSlice[self.election.contests[contest_name].winners, :], **{'color' : 'blue'})
        self.data_frame[contest_name] = df.style.set_properties(subset = pd.IndexSlice[self.election.contests[contest_name].winners, :], **{'color' : 'blue'})
        return self.data_frame[contest_name]

    def set_ele(self, results, ballots_cast=None):
        election = {}
        # election["alpha"] = risk_limit
        # election["delta"] = 1.0
        election["name"] = "x"
        contest_name = "x"
        # election["round_schedule"] = round_schedule
        if ballots_cast is None:
            ballots_cast = sum(results)
        else:
            if ballots_cast < sum(results):
                Exception("wrong number of ballots cast")

        # election["ballots_cast"] = ballots_cast
        election["total_ballots"] = ballots_cast
        candidates = ["A", "B"]
        # results = {1981473, 95369}
        tally = {}
        for can, votes in zip(candidates, results):
            tally[can] = votes


        reported_winner = ["A"]

        if results[1] > results[0]:
            reported_winner = ["B"]

        # tallyj = json.dumps(tally)
        # election["contests"] = f'{{"{contest_name}": {{"contest_ballots": {ballots_cast}, "tally": {tallyj}, "num_winners": {winners}, "reported_winners": ["A"]}} }}'
        # election["data"] = f'{{"name": "x", "total_ballots": {ballots_cast}, "contests" : {election["contests"]}}}'
        election["contests"] = {contest_name: {"contest_ballots": ballots_cast, "tally": tally, "num_winners": 1,
                                               "reported_winners": reported_winner}}
        election["data"] = {"name": "x", "total_ballots": ballots_cast, "contests": election["contests"]}
        # print(election["contests"])
        # json.loads(election["contests"])
        # print(election["data"])
        # print(election["data"])
        election["candidates"] = candidates
        election["results"] = results
        # election["winners"] = ["A"]
        # election_object = Contest(election["data"])
        # return election_object
        # print(str(election))
        return election

