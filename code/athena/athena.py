import logging
from scipy.stats import binom
from scipy.signal import fftconvolve
import math


class AthenaAudit():
    """
    A class used to represent an AthenaAudit

    ...

    Methods
    -------
    next_round_prob(self, margin, round_size_prev, round_size, kmin, prob_table_prev)
        Computed the distribution probability at the end of the next round

    audit(self, audit_type, margin, alpha, round_schedule)
        Computes probabilities of stopping, risk and kmins for given parameters and audit_type

    athena(self, margin, alpha, round_schedule)
        Computes parameters for ATHENA audit

    arlo(self, margin, alpha, round_schedule)
        Computes parameters for ARLO audit

    bravo(self, margin, alpha, round_schedule)
        Computes parameters for BRAVO audit

    find_next_round_size(self, margin, alpha, round_schedule, quant, round_min)
        Computes expected round size such that audit would end with probability quant

    find_next_round_sizes(self, margin, alpha, round_schedule, quants)
        Computes expected round sizes for a given list of stopping probabilities (quants)

    """

    check_delta = 0
    check_sum = 0
    check_memory = 0

    def set_checks(self, audit_type):
        if audit_type.lower() in {"bravo", "wald", "arlo"}:
            self.check_delta = 1
            self.check_sum = 0
            self.check_memory = 0
        elif audit_type.lower() in {"athena"}:
            self.check_delta = 1
            self.check_sum = 1
            self.check_memory = 0
        elif audit_type.lower() in {"minerva"}:
            self.check_delta = 0
            self.check_sum = 1
            self.check_memory = 0
        elif audit_type.lower() in {"metis"}:
            self.check_delta = 0
            self.check_sum = 1
            self.check_memory = 1

        #print("delta check: %s\nsum check: %s\nmemory check: %s" % (self.check_delta, self.check_sum, self.check_memory))


    def next_round_prob(self, margin, round_size_prev, round_size, prob_table_prev):
        """
        Parameters
        ----------
        :param margin: margin of a given race (float in [0, 1])
        :param round_size_prev: the size of the previous round
        :param round_size: the size of the current round
        :param prob_table_prev: the probability distribution at the begining of the current round
        :return: prob_table: the probability distribution at the end of the current round is returned
        """
        '''# This approach comes from GrantMcClearn: 
        https://github.com/gwexploratoryaudits/brla_explore/blob/grant/src/athena.py
        For the following paramters:
            *time python3 athena.py -n 2016_Minnesota -c Clinton Trump -b 1367825 1323232 --rounds 10000 20000*
            runs in:
            - real	0m0,377s
            - user	0m0,787s
            - sys	0m0,317s
            while            
             *time python3 aurror.py -n 2016_Minnesota -c Clinton Trump -b 1367825 1323232 --rounds 10000 20000*
            runs in:
            - real	133m57,646s
            - user	133m29,192s
            - sys	0m2,683s
            (on a machine with: Ubuntu 18.04 / i7-8850H / 32GB)
        '''

        p = (1+margin)/2
        draws_dist = binom.pmf(range(0, (round_size - round_size_prev) + 1), (round_size - round_size_prev), p)
        return fftconvolve(prob_table_prev, draws_dist)


    def next_round_prob_bravo(self, margin, round_size_prev, round_size, kmin_first, kmin, prob_table_prev):
        """
        Parameters
        ----------
        :param margin: margin of a given race (float in [0, 1])
        :param round_size_prev: the size of the previous round
        :param round_size: the size of the current round
        :param kmin_first: the kmin for the first round
        :param kmin: the value of previous kmin
        :param prob_table_prev: the probability distribution at the begining of the current round
        :return: prob_table: the probability distribution at the end of the current round is returned
        """


        prob_table = [0] * (round_size + 1)
        for i in range(kmin + 1):
            for j in range(min(round_size + 1, round_size - round_size_prev + kmin + 1)):
                prob_table[j] = prob_table[j] + binom.pmf(j-i, round_size - round_size_prev, (1+margin)/2) * prob_table_prev[i]

        return prob_table


    def athena(self, margin, alpha, delta, round_schedule):
        """
        Sets audit_type to **athena** and calls audit(...) method
        """
        return self.audit("athena", margin, alpha, delta, round_schedule)

    def metis(self, margin, alpha, delta, round_schedule):
        """
        Sets audit_type to **metis** and calls audit(...) method
        """
        return self.audit("metis", margin, alpha, delta, round_schedule)

    def minerva(self, margin, alpha, round_schedule):
        """
        Sets audit_type to **minerva** and calls audit(...) method
        """
        return self.audit("minerva", margin, alpha, alpha, round_schedule)

    def bravo(self, margin, alpha, round_schedule):
        """
        Function simply calls athena(...) method but as a round schedule a list of [1, 2, 3, ..., max] is given.
        For more info, see athena(...) method.

        Parameters
        ----------
        :param round_schedule: is a list of increasing natural numbers that correspond to number of relevant votes drawn
        """
        return self.athena(margin, alpha, alpha, list(range(1, round_schedule[-1] + 1)))

    def arlo(self, margin, alpha, round_schedule):
        """
        Sets audit type to **arlo** and calls audit(...) method
        """
        return self.audit("arlo", margin, alpha, alpha, round_schedule)


    def wald_k_min(self, sample_size, margin, delta):
        """
        Returns Bravo/Wald's kmin for the sample size m, margin x and risk alpha
        :param sample_size: (integer) number of ballots drawn during the audit so far
        :param margin: (float 0<margin<1) margin of the victory
        :param delta: (float 0<delta<1) risk limit for Wald's test
        :return:
        """
        bkm = min(math.ceil(math.log(delta * pow(1 - margin, sample_size), (1-margin)/(1+margin))), sample_size + 1)
        #if bkm > sample_size:
        #    return 0
        #else:
        return bkm


    def audit(self, audit_type, margin, alpha, delta, round_schedule):
        """
        Parameters
        ----------
        :param margin: margin of a given race (float in [0, 1])
        :param alpha: is the risk limit (float in (0, 1))
        :param delta: is the worst case ratio ... !TODO
        :param round_schedule: is a list of increasing natural numbers that correspond to number of relevant votes drawn
        :return:

            * kmins - list of kmins (corresponding to the round_schedule)
            * prob_sum - list of stopping probabilities
            * prob_tied_sum - list of stopping probabilities for tied elections (risk)
        """
        #print("Starting audit for %s %s %s %s %s" % (audit_type, margin, alpha, delta, round_schedule))

        self.set_checks(audit_type)

        round_schedule = [0] + round_schedule
        number_of_rounds = len(round_schedule)
        prob_table_prev = [1]
        prob_tied_table_prev = [1]
        kmins = [0] * number_of_rounds
        prob_sum = [0] * number_of_rounds
        prob_tied_sum = [0] * number_of_rounds
        deltas = [0] * number_of_rounds



        for round in range(1, number_of_rounds):
            prob_table = self.next_round_prob(margin, round_schedule[round - 1], round_schedule[round], prob_table_prev)
            prob_tied_table = self.next_round_prob(0, round_schedule[round - 1], round_schedule[round], prob_tied_table_prev)

            kmin_found = False
            kmin_candidate = math.floor(round_schedule[round]/2)

            while kmin_found is False and kmin_candidate <= round_schedule[round]:
                if self.check_delta * delta * prob_table[kmin_candidate] >= self.check_delta * prob_tied_table[kmin_candidate] \
                        and self.check_sum * alpha * (sum(prob_table[kmin_candidate:len(prob_table)]) + self.check_memory * prob_sum[round - 1]) >= \
                            self.check_sum * (sum(prob_tied_table[kmin_candidate:len(prob_tied_table)]) + self.check_memory * prob_tied_sum[round - 1]):
                    kmin_found = True
                    kmins[round] = kmin_candidate
                    prob_sum[round] = sum(prob_table[kmin_candidate:len(prob_table)]) + prob_sum[round - 1]
                    prob_tied_sum[round] = sum(prob_tied_table[kmin_candidate:len(prob_tied_table)]) + prob_tied_sum[round - 1]
                    if prob_table[kmin_candidate] > 0:
                        deltas[round] = prob_tied_table[kmin_candidate] /  prob_table[kmin_candidate]
                else:
                    kmin_candidate = kmin_candidate + 1



            # this means that there are 0 chance of stopping in the given round -- the kmin is unreachable
            if kmin_found is False:
                    prob_sum[round] =  prob_sum[round - 1]
                    prob_tied_sum[round] =  prob_tied_sum[round - 1]

            # cleaning prob_table/prob_tied_table - there are no walks at and above kmin
            for i in range(kmin_candidate, round_schedule[round] + 1):
                prob_table[i] = 0
                prob_tied_table[i] = 0

            prob_table_prev = prob_table
            prob_tied_table_prev = prob_tied_table


        # Define upper tolerance for probability tests to allow some fudge
        one_tol = 1.0 + 1e-9

        assert self.non_decreasing(kmins[1:]), f'Internal error: kmin values not monotonic: {kmins[1:]}'
        assert all(0.0 <= prob <= one_tol for prob in prob_sum[1:]), f'Internal error: prob_sum <0 or >1: {prob_sum[1:]}'
        assert all(0.0 <= prob <= one_tol for prob in prob_tied_sum[1:]), f'Internal error: prob_tied_sum <0 or >1: {prob_tied_sum[1:]}'
        assert self.non_decreasing(prob_sum[1:]), f'Internal error: prob_sum values not monotonic: {prob_sum[1:]}'
        assert self.non_decreasing(prob_tied_sum[1:]), f'Internal error: prob_tied_sum values not monotonic: {prob_tied_sum[1:]}'

        return {"kmins": kmins[1:len(kmins)], "prob_sum": prob_sum[1:len(prob_sum)], "prob_tied_sum": prob_tied_sum[1:len(prob_tied_sum)], "deltas": deltas[1:len(kmins)]}

    def find_next_round_size(self, audit_type, margin, alpha, delta, round_schedule, quant, round_min, ballots_cast):
        """
        For given audit parameters, computes the expected size of the next round.

        Parameters
        ----------
        :param margin: margin for that race
        :param alpha: risk limit
        :param delta: delta parameter
        :param round_schedule: round schedule
        :param quant: desired probability of stopping in the next round
        :param round_min: min size of the next round
        :return:

            * size - the size of the next round
            * prob_stop - the probability of
        """
        #print("find_next_round_size")
        if quant <= .9  and len(round_schedule) < 1:
            round_max = math.ceil((18 * math.log(alpha))/(margin *  (math.log(1 - margin) - math.log(1 + margin))))
        else:
            round_max = 1 * ballots_cast
        new_round_schedule = round_schedule + [round_max]
        result = self.audit(audit_type, margin, alpha, delta, new_round_schedule)
        #print("audit results: %s" % (result))
        prob_table = result["prob_sum"]
        stopping_probability_max = self.relative_prob(prob_table)
        if stopping_probability_max < quant:
            logging.warning("FULL RECOUNT is suggested!")
            logging.warning("Probability of stopping at: %s is %s" % (new_round_schedule, stopping_probability_max))
            return {"size": round_max, "prob_stop": stopping_probability_max}

        #print("here we are")

        if len(round_schedule) > 0:
            round_candidate = round_schedule[-1] + math.floor(( round_max)/2)
        else:
            round_candidate = math.floor((round_max)/2)

        round_min_found = False


        while round_min_found is False:
            new_round_schedule = round_schedule + [round_candidate]
            result = self.audit(audit_type, margin, alpha, delta, new_round_schedule)
            prob_table = result["prob_sum"]
            #print("%s\t%s\t%s\t%s\t%s\t%s" % (round_min, round_candidate, round_max, new_round_schedule, prob_table, self.relative_prob(prob_table)))
            #print("\t" + str(prob_table))

            if self.relative_prob(prob_table) >= quant:
                round_max = round_candidate
                if len(round_schedule) > 0:
                    round_candidate = round_schedule[-1] + math.floor((round_max - round_schedule[-1])/2)
                else:
                    round_candidate = math.floor((round_max)/2)
            else:
                round_min = round_candidate
                round_min_found = True

        #print("\t\t->\t" + str(round_min) + "\t" + str(round_max))

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
            result = self.audit(audit_type, margin, alpha, delta, new_round_schedule)
            prob_table = result["prob_sum"]
            #print("\t%s\t%s\t%s\t%s\t%s" % (round_min, round_candidate, round_max, new_round_schedule, prob_table))


            if self.relative_prob(prob_table) <= quant:
                round_min = round_candidate
            else:
                round_max = round_candidate

            # TODO: change "10" into something parametrized
            if (self.relative_prob(prob_table) - quant > 0 and self.relative_prob(prob_table) - quant < .01) or round_max - round_min <= 1:
                round_candidate = round_max
                new_round_schedule = round_schedule + [round_candidate]
                result = self.audit(audit_type, margin, alpha, delta, new_round_schedule)
                prob_table = result["prob_sum"]
                #print("\t%s\t%s\t%s\t%s\t%s" % (round_min, round_candidate, round_max, new_round_schedule, prob_table))
                break

        return {"size": round_candidate, "prob_stop": prob_table[-1]}

    def find_next_round_sizes(self, audit_type, margin, alpha, delta, round_schedule, quants, ballots_cast):
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
        rounds = []
        prob_stop = []
        for quant in quants:
            #print("starting for: " + str(quant))
            results = self.find_next_round_size(audit_type, margin, alpha, delta, round_schedule, quant, 1, ballots_cast)
            new_round = results["size"]
            new_round_schedule = round_schedule + [new_round]
            #print("\t" + str(quant) + "\t" + str(new_round_schedule))
            round_candidate = results["size"]
            rounds.append(round_candidate)
            prob_stop.append(results["prob_stop"])

        return {"rounds" : rounds, "prob_stop" : prob_stop}

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

    def find_kmins_for_risk(self, audit_kmins, actual_kmins):

        kmins_goal_real = []
        rewrite_on = 1
        test_passed = 0

        for audit_k, actual_k in zip(audit_kmins, actual_kmins):
            if audit_k <= actual_k and audit_k > 0:
                test_passed = 1

        for i in range(len(actual_kmins)-1):
            if rewrite_on == 1:
                if audit_kmins[i] <= actual_kmins[i]:
                    kmins_goal_real.append(actual_kmins[i])
                    rewrite_on = 0
                else:
                    kmins_goal_real.append(audit_kmins[i])

        if rewrite_on == 1:
            kmins_goal_real.append(actual_kmins[len(actual_kmins)-1])

        return {"kmins" : kmins_goal_real, "passed": test_passed}


    def estimate_risk(self, margin, kmins, round_schedule, audit_observations):
        """
        Parameters
        ----------
        :param kmins: list of kmins
        :param round_schedule: is a list of increasing natural numbers that correspond to number of relevant votes drawn
        :return:
            * prob_tied_sum - list of stopping probabilities for tied elections (risk)
        """
        round_schedule = [0] + round_schedule
        kmins = [0] + kmins
        audit_observations = [0] + audit_observations
        number_of_rounds = min(len(audit_observations), len(round_schedule))
        prob_table_prev = [1]
        prob_sum = [0] * number_of_rounds
        prob_tied_table_prev = [1]
        prob_tied_sum = [0] * number_of_rounds
        audit_round_pstop = [0] * number_of_rounds
        audit_round_risk = [0] * number_of_rounds
        audit_ratio = [0] * number_of_rounds

        deltas = []#0] * (number_of_rounds + 1)

        for round in range(1, number_of_rounds):
            prob_table = self.next_round_prob(margin, round_schedule[round - 1], round_schedule[round], prob_table_prev)
            prob_tied_table = self.next_round_prob(0, round_schedule[round - 1], round_schedule[round], prob_tied_table_prev)

            prob_sum[round] = sum(prob_table[kmins[round]:len(prob_table)]) + prob_sum[round - 1]
            prob_tied_sum[round] = sum(prob_tied_table[kmins[round]:len(prob_tied_table)]) + prob_tied_sum[round - 1]

            audit_round_pstop[round] = sum(prob_table[audit_observations[round]:len(prob_table)])
            audit_round_risk[round] = sum(prob_tied_table[audit_observations[round]:len(prob_tied_table)])
            if audit_round_pstop[round] > 0:
                audit_ratio[round] = audit_round_risk[round] / audit_round_pstop[round]




            if prob_table[kmins[round]] is not 0 and round < len(audit_observations):
                if prob_table[audit_observations[round]] > 0:
                    deltas.append(abs(prob_tied_table[audit_observations[round]] / prob_table[audit_observations[round]]))

            # cleaning prob_table/prob_tied_table
            for i in range(kmins[round], round_schedule[round] + 1):
                prob_table[i] = 0
                prob_tied_table[i] = 0

            prob_table_prev = prob_table
            prob_tied_table_prev = prob_tied_table


        ratio = []
        for i, p, pt in zip(range(len(prob_sum)), prob_sum[1:len(prob_sum)], prob_tied_sum[1:len(prob_tied_sum)]):
            if p > 0:
                ratio.append(pt / p)
            else:
                ratio.append(0)


        return {"prob_sum": prob_sum[1:len(prob_sum)], "prob_tied_sum": prob_tied_sum[1:len(prob_tied_sum)], "audit_ratio": audit_ratio[1:len(audit_ratio)], "ratio": ratio, "deltas": deltas}

    def non_decreasing(self, l):
        """Check that positive values in list l are mononotonic.
        Ignore zero and negative sentinal values
        Allow a tolerance of 10^-9.
        """

        tol = 1e-9

        pos_l = [val for val in l if val > 0]
        return all(x <= (y + tol) for x, y in zip(pos_l, pos_l[1:]))
