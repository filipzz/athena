from scipy.stats import binom
import math

class AurrorAudit():
    """
    A class used to represent an AurrorAudit

    ...

    Methods
    -------
    next_round_prob(self, margin, round_size_prev, round_size, kmin, prob_table_prev)
        Computed the distribution probability at the end of the next round

    audit(self, audit_type, margin, alpha, round_schedule)
        Computes probabilities of stopping, risk and kmins for given parameters and audit_type

    aurror(self, margin, alpha, round_schedule)
        Computes parameters for AURROR audit

    arlo(self, margin, alpha, round_schedule)
        Computes parameters for ARLO audit

    bravo(self, margin, alpha, round_schedule)
        Computes parameters for BRAVO audit

    find_next_round_size(self, margin, alpha, round_schedule, quant, round_min)
        Computes expected round size such that audit would end with probability quant

    find_next_round_sizes(self, margin, alpha, round_schedule, quants)
        Computes expected round sizes for a given list of stopping probabilities (quants)

    """

    def next_round_prob(self, margin, round_size_prev, round_size, kmin, prob_table_prev):
        """
        Parameters
        ----------
        :param margin: margin of a given race (float in [0, 1])
        :param round_size_prev: the size of the previous round
        :param round_size: the size of the current round
        :param kmin: the value of previous kmin
        :param prob_table_prev: the probability distribution at the begining of the current round
        :return: prob_table: the probability distribution at the end of the current round is returned
        """



        prob_table = [0] * (round_size + 1)
        #TODO: short fix for checking correctness of limit
        #for i in range(kmin + 1):
        for i in range(round_size_prev + 1):
            for j in range(round_size + 1):
                prob_table[j] = prob_table[j] + binom.pmf(j-i, round_size - round_size_prev, (1+margin)/2) * prob_table_prev[i]

        #print("\t%s\t%s" % (margin, prob_table_prev))
        #print("\t\t%s" % (prob_table))
        return prob_table

    def aurror(self, margin, alpha, round_schedule):
        """
        Sets audit_type to **aurror** and calls audit(...) method
        """
        return self.audit("aurror", margin, alpha, round_schedule)

    def bravo(self, margin, alpha, round_schedule):
        """
        Function simply calls aurror(...) method but as a round schedule a list of [1, 2, 3, ..., max] is given.
        For more info, see aurror(...) method.

        Parameters
        ----------
        :param round_schedule: is a list of increasing natural numbers that correspond to number of relevant votes drawn
        """
        return self.aurror(margin, alpha, list(range(1, round_schedule[-1] + 1)))


    def arlo(self, margin, alpha, round_schedule):
        """
        Sets audit type to **arlo** and calls audit(...) method
        """
        return self.audit("arlo", margin, alpha, round_schedule)

    def audit(self, audit_type, margin, alpha, round_schedule):
        """
        Parameters
        ----------
        :param margin: margin of a given race (float in [0, 1])
        :param alpha: is the risk limit (float in (0, 1))
        :param round_schedule: is a list of increasing natural numbers that correspond to number of relevant votes drawn
        :return:

            * kmins - list of kmins (corresponding to the round_schedule)
            * prob_sum - list of stopping probabilities
            * prob_tied_sum - list of stopping probabilities for tied elections (risk)
        """
        round_schedule = [0] + round_schedule
        number_of_rounds = len(round_schedule)
        prob_table_prev = [1]
        prob_tied_table_prev = [1]
        kmins = [0] * number_of_rounds
        prob_sum = [0] * number_of_rounds
        prob_tied_sum = [0] * number_of_rounds

        for round in range(1,number_of_rounds):
            #print("\n%s" % (round))
            prob_table = self.next_round_prob(margin, round_schedule[round - 1], round_schedule[round], kmins[round - 1], prob_table_prev)
            prob_tied_table = self.next_round_prob(0, round_schedule[round - 1], round_schedule[round], kmins[round - 1], prob_tied_table_prev)
            #print("\n")

            kmin_found = False
            kmin_candidate = math.floor(round_schedule[round]/2)
            while kmin_found == False and kmin_candidate <= round_schedule[round]:
                if audit_type == "aurror": #but this also works for bravo
                    # prob_table[kmin_candidate] >= prob_tied_table[kmin_candidate] condition added
                    if prob_table[kmin_candidate] >= prob_tied_table[kmin_candidate] and alpha * (sum(prob_table[kmin_candidate:len(prob_table)])) >= (sum(prob_tied_table[kmin_candidate:len(prob_tied_table)])):
                        kmin_found = True
                        kmins[round] = kmin_candidate
                        prob_sum[round] = sum(prob_table[kmin_candidate:len(prob_table)]) + prob_sum[round - 1]
                        prob_tied_sum[round] = sum(prob_tied_table[kmin_candidate:len(prob_tied_table)]) + prob_tied_sum[round - 1]
                    else:
                        kmin_candidate = kmin_candidate + 1
                elif audit_type == "arlo":
                    if alpha * ((prob_table[kmin_candidate])) >= ((prob_tied_table[kmin_candidate])):
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



    def find_next_round_size(self, margin, alpha, round_schedule, quant, round_min):
        """
        For given audit parameters, computes the expected size of the next round.

        Parameters
        ----------
        :param margin: margin for that race
        :param alpha: risk limit
        :param round_schedule: round schedule
        :param quant: desired probability of stopping in the next round
        :param round_min: min size of the next round
        :return:

            * size - the size of the next round
            * prob_stop - the probability of
        """
        if len(round_schedule) > 0:
            round_candidate = 2 * round_schedule[-1]
            round_min = round_schedule[-1]
            #round_max = round_candidate
        else:
            round_candidate = round_min
            #round_max = 2 * round_candidate

        # TODO: make sure that round_min leads to the situation where audit with a given round schedule extended with round_min stops with probability less than quant

        #print("\tfnrs:\t" + str(quant) + "\t" + str(round_min) + "\t" + str(round_candidate))

        # first loop tries to find round size that is large enough to have the probability of stopping larger than quant
        while True:
            new_round_schedule = round_schedule + [round_candidate]
            result = self.aurror(margin, alpha, new_round_schedule)
            prob_table = result["prob_sum"]
            #print("\t\tfirst loop:\t" +  str(round_min) + "\t" + str(round_candidate) + "\t" + str(prob_table[-1]))

            #if prob_table[-1] >= quant:
            if self.relative_prob(prob_table) >= quant:
                round_max = round_candidate
                break
            else:
                round_min = round_candidate
                round_candidate = 2 * round_min

        # the main loop:
        # * we have round_min (for which the probability of stopping is smaller than quant), and
        # * we have round_max (for which the probability of stopping is larger than quant)
        # we perform binary search to find a candidate (round_candidate) for the next round size
        # It may happen that this value:
        # * will not be the first round size that satisfied our requirement
        # * it may(?)  be slightly below the quant (because of non-monotonicity)
        while True:
            round_candidate = round((round_max + round_min)/2)
            new_round_schedule = round_schedule + [round_candidate]
            result = self.aurror(margin, alpha, new_round_schedule)
            prob_table = result["prob_sum"]
            #print("\t\tmain loop:\t" + str(round_min) + "\t" + str(round_candidate) + "\t" + str(round_max) + "\t" + str(prob_table[-1]))

            #if prob_table[-1] <= quant:
            if self.relative_prob(prob_table) <=  quant:
                round_min = round_candidate
            else:
                round_max = round_candidate

            # TODO: change "10" into something parametrized
            #if (prob_table[-1] - quant > 0 and prob_table[-1] - quant < .01) or round_max - round_min <= 2:
            if (self.relative_prob(prob_table) - quant > 0 and self.relative_prob(prob_table) - quant < .01) or round_max - round_min <= 2:
                break

        #print(str(self.relative_prob(prob_table)))
        #print(str(prob_table))

        return {"size" : round_candidate, "prob_stop" : prob_table[-1]}


    def find_next_round_sizes(self, margin, alpha, round_schedule, quants):
        '''
        For a given list of possible stopping probabilities (called quants e.g., quants = [.7, .8, .9]) returns a list of
        next round sizes  for which probability of stoping is larger than quants

        ...

        Parameters
        ----------
        :param margin: margin for given race
        :param alpha: risk limit
        :param round_schedule: round schedule (so far)
        :param quants: list of desired stopping probabilities
        :return: a list of expected round sizes
        '''
        round_candidate = 10
        rounds = []
        for quant in quants:
            results = self.find_next_round_size(margin, alpha, round_schedule, quant, round_candidate)
            new_round = results["size"]
            new_round_schedule = round_schedule + [new_round]
            print("\t" + str(quant) + "\t" + str(new_round_schedule))
            round_candidate = results["size"]
            rounds.append(round_candidate)

        return rounds



    def relative_prob(self, prob_table):
        '''
        Helper function, returning the conditional probability of the last round success, from a list representing
        cumulative probability

        :param prob_table: list of probabilities of stopping in consecurtive rounds
        :return: probability of stopping in the last round conditioned by not stopping in the previous round
        '''
        if len(prob_table) == 1:
            return prob_table[-1]
        else:
            prob_prev = prob_table[-2]
            prob_last = prob_table[-1]
            prob_total = 1 - prob_prev
            prob_gain = prob_last - prob_prev
            return prob_gain / prob_total
