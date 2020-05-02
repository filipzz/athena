import logging
import math

from .athena import AthenaAudit
from .election import Election

class Audit():

    def __init__(self, audit_type, alpha, delta = 1):
        self.audit_type = audit_type
        self.elections = []
        self.round_schedule = []
        self.audit_observations = []
        self.audit_kmins = []
        self.alpha = alpha
        self.delta = delta




    def add_election(self, election):
        new_election = Election(election)
        self.election = new_election

    def add_round_schedule(self, round_schedule):
        self.round_schedule = round_schedule


    def extend_round_schedule(self, next_round):
        logging.info("Current round schedule:\t%s" % (self.election.round_schedule))
        self.round_schedule.append(next_round)
        logging.info("New round schedule:\t%s" % (self.election.round_schedule))

    def find_next_round_size(self, pstop_goals):
        logging.info("setting round schedule")

        found_solutions = {}
        future_round_sizes = [0] * len(pstop_goals)
        #future_prob_stop = [0] * len(pstop_goals)

        for i in range(len(self.election.candidates)):
            ballots_i = self.election.results[i]
            candidate_i = self.election.candidates[i]
            for j in range(i + 1, len(self.election.candidates)):
                ballots_j = self.election.results[j]
                candidate_j = self.election.candidates[j]

                logging.info("\n\n%s (%s) vs %s (%s)" % (candidate_i, (ballots_i), candidate_j, (ballots_j)))
                bc = ballots_i + ballots_j
                scalling_ratio = self.election.ballots_cast / bc
                winner = max(ballots_i, ballots_j)
                logging.info("\tmargin:\t" + str((winner - min(ballots_i, ballots_j))/bc))
                rs = []
                for x in self.round_schedule:
                    y = math.floor(x * bc / self.election.ballots_cast)
                    rs.append(y)

                margin = (2 * winner - bc)/bc

                audit_object = AthenaAudit()

                logging.info("\tpstop goals: " + str(pstop_goals))
                logging.info("\tscaled round schedule: " + str(rs))
                rescaled = []
                next_round_sizes = audit_object.find_next_round_sizes(self.audit_type, margin, self.alpha, self.delta, rs, pstop_goals, bc)
                for i, pstop_goal, next_round, prob_stop in zip(range(len(pstop_goals)), pstop_goals, next_round_sizes["rounds"], next_round_sizes["prob_stop"]):
                    rs = [] + self.round_schedule
                    next_round_rescaled = math.ceil(next_round * scalling_ratio)
                    rs.append(next_round_rescaled)
                    rescaled.append(next_round_rescaled)
                    future_round_sizes[i] = max(future_round_sizes[i], next_round_rescaled)
                    logging.info("\t\t%s:\t%s\t%s" % (pstop_goal, rs, prob_stop))

                found_solutions[candidate_i + "-" + candidate_j] = {"pstop_goal": pstop_goals, "next_round_sizes": rescaled, "prob_stop": next_round_sizes["prob_stop"]}

            return {"detailed" : found_solutions, "future_round_sizes" : future_round_sizes}

    def find_risk(self, audit_observations):
        for i in range(len(self.election.candidates)):
            ballots_i = self.election.results[i]
            candidate_i = self.election.candidates[i]
            for j in range(i + 1, len(self.election.candidates)):
                ballots_j = self.election.results[j]
                candidate_j = self.election.candidates[j]

                logging.info("\n\n%s (%s) vs %s (%s)" % (candidate_i, (ballots_i), candidate_j, (ballots_j)))
                bc = ballots_i + ballots_j
                winner = max(ballots_i, ballots_j)
                logging.info("\tmargin:\t" + str((winner - min(ballots_i, ballots_j))/bc))
                rs = []

                for x in self.round_schedule:
                    y = math.floor(x * bc / self.election.ballots_cast)
                    rs.append(y)

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

                risk_goal = audit_athena["prob_tied_sum"]
                self.audit_kmins = audit_athena["kmins"]

                logging.info(str(audit_athena))

                test_info = audit_object.find_kmins_for_risk(self.audit_kmins, audit_observations)

                logging.info("find_kmins_for_risk")
                logging.info(str(test_info))

                logging.info("\n\tAUDIT result:")
                logging.info("\t\tobserved:\t" + str(audit_observations))
                logging.info("\t\trequired:\t" + str(self.audit_kmins))

                if test_info["passed"] == 1:
                    logging.info("\n\t\tTest passed\n")
                else:
                    logging.info("\n\t\tTest FAILED\n")

                #w = audit_object.estimate_risk(margin, actual_kmins, round_schedule)
                #w = audit_object.estimate_risk(margin, test_info["kmins"], self.round_schedule, audit_observations)
                w = audit_object.estimate_risk(margin, self.audit_kmins, self.round_schedule, audit_observations)
                #logging.info(str(w))
                #ratio = w["ratio"]
                deltas = w["deltas"]
                audit_risk = min(filter(lambda x: x > 0, w["audit_ratio"]))
                #logging.info(str(w))
                #logging.info("Risk spent:\t%s" % (ratio[-1]))
                logging.info("Delta:\t\t%s" % (deltas[-1]))
                logging.info("AUDIT risk:\t%s" % (audit_risk))

                return {"risk": audit_risk, "delta": deltas[-1],  "passed": test_info["passed"], "observed": audit_observations, "required": self.audit_kmins}


