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
    audit_type = ""
    margin = 0.0
    alpha = 0.1

    def __init__(self, audit_type, alpha, delta):
        """
        Parameters
        ----------
        :param audit_type:
        :param alpha: is the risk limit (float in (0, 1))
        :param delta: is the worst case ratio ... !TODO
        """
        self.alpha = alpha
        self.delta = delta
        self.audit_type = audit_type
        if self.audit_type.lower() in {"bravo", "wald", "arlo"}:
            self.delta = self.alpha
        self.set_checks(audit_type)

        """Storing information about the probability distribution in the previous round of an audit"""
        self.prob_distribution_margin = [1.0]
        self.prob_distribution_tied = [1.0]

        """Storing information about the probabilities of stopping in a given round"""
        self.pstop_round = [0.0]
        self.pstop_tied_round = [0.0]


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
        bkm = math.ceil(math.log(delta * math.pow(1 - margin, sample_size), (1-margin)/(1+margin)))
        #if bkm > sample_size:
        #    return 0
        #else:
        return bkm


    #def audit(self, audit_type, margin, alpha, delta, round_schedule):
    def audit(self, margin, round_schedule):
        """
        Parameters
        ----------
        :param margin: margin of a given race (float in [0, 1])
        :param round_schedule: is a list of increasing natural numbers that correspond to number of relevant votes drawn
        :return:

            * kmins - list of kmins (corresponding to the round_schedule)
            * prob_sum - list of stopping probabilities
            * prob_tied_sum - list of stopping probabilities for tied elections (risk)
        """
        self.margin = margin


        round_schedule = [0] + round_schedule
        number_of_rounds = len(round_schedule)
        prob_table_prev = [1]
        prob_tied_table_prev = [1]
        kmins = [0] * number_of_rounds
        prob_sum = [0] * number_of_rounds
        prob_tied_sum = [0] * number_of_rounds
        deltas = [0] * number_of_rounds

        print(str(round_schedule))


        for round in range(1, number_of_rounds):
            prob_table = self.next_round_prob(margin, round_schedule[round - 1], round_schedule[round], prob_table_prev)
            prob_tied_table = self.next_round_prob(0, round_schedule[round - 1], round_schedule[round], prob_tied_table_prev)

            kmin_found = False
            kmin_candidate = math.floor(round_schedule[round]/2)

            while kmin_found is False and kmin_candidate <= round_schedule[round]:
                print("\t" + str(kmin_candidate))
                if self.check_delta * self.delta * prob_table[kmin_candidate] >= self.check_delta * prob_tied_table[kmin_candidate] \
                        and self.check_sum * self.alpha * (sum(prob_table[kmin_candidate:len(prob_table)]) + self.check_memory * prob_sum[round - 1]) >= \
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

            self.pstop_round.append(sum(prob_table_prev))
            self.pstop_tied_round.append(sum(prob_tied_sum))

        self.prob_distribution_margin = prob_table_prev
        self.prob_distribution_tied = prob_tied_table_prev

        # Define upper tolerance for probability tests to allow some fudge
        one_tol = 1.0 + 1e-8

        #assert self.non_decreasing(kmins[1:]), f'Internal error: kmin values not monotonic: {kmins[1:]}'
        assert all(0.0 <= prob <= one_tol for prob in prob_sum[1:]), f'Internal error: prob_sum <0 or >1: {prob_sum[1:]}'
        assert all(0.0 <= prob <= one_tol for prob in prob_tied_sum[1:]), f'Internal error: prob_tied_sum <0 or >1: {prob_tied_sum[1:]}'
        assert self.non_decreasing(prob_sum[1:]), f'Internal error: prob_sum values not monotonic: {prob_sum[1:]}'
        assert self.non_decreasing(prob_tied_sum[1:]), f'Internal error: prob_tied_sum values not monotonic: {prob_tied_sum[1:]}'

        return {"kmins": kmins[1:len(kmins)], "prob_sum": prob_sum[1:len(prob_sum)], "prob_tied_sum": prob_tied_sum[1:len(prob_tied_sum)], "deltas": deltas[1:len(kmins)]}

    def find_next_round_kmin(self, margin, new_round_schedule):
        round_candidate = new_round_schedule[-1]
        if len(new_round_schedule) > 1:
            round_size_prev = new_round_schedule[-2]
        else:
            round_size_prev = 0

        p = (1+margin)/2
        draws_dist = binom.pmf(range(0, (round_candidate - round_size_prev) + 1), (round_candidate - round_size_prev), p)
        prob_table = fftconvolve(self.prob_distribution_margin, draws_dist)

        p0 = 0.5
        draws_dist_tied = binom.pmf(range(0, (round_candidate - round_size_prev) + 1), (round_candidate - round_size_prev), p0)
        prob_table_tied = fftconvolve(self.prob_distribution_tied, draws_dist_tied)

        kmin_found = False

        #TODO: verify lower limit
        #kmin_candidate = math.floor(round_candidate / 2)
        if self.audit_type.lower() in {"athena", "bravo", "arlo"}:
            kmin_candidate = math.floor((.5 + p)/2 * round_candidate)
        else:
            #TODO: find the correct lower bound for minerva/metis
            kmin_candidate = max(math.ceil(round_candidate / 2), math.floor((.5 + p)/2 * round_candidate) - 10)

        #TODO: verify upper limit
        while kmin_found is False and kmin_candidate <= math.ceil((1+2 * margin) * round_candidate/2) and kmin_candidate <= new_round_schedule[-1]:
            if self.check_delta * self.delta * prob_table[kmin_candidate] >= self.check_delta * prob_table_tied[kmin_candidate] \
                    and self.check_sum * self.alpha * (sum(prob_table[kmin_candidate:]) + self.check_memory * sum(self.pstop_round)) >= \
                    self.check_sum * (sum(prob_table_tied[kmin_candidate:]) + self.check_memory * sum(self.pstop_tied_round)):
                kmin_found = True
            else:
                kmin_candidate = kmin_candidate + 1

        if kmin_found:
            if prob_table[kmin_candidate] > 0:
                delta = prob_table_tied[kmin_candidate]/prob_table[kmin_candidate]
            else:
                delta = None
            return {
                "kmin": kmin_candidate,
                "prob_stop": sum(prob_table[kmin_candidate:]),
                "prob_stop_tied": sum(prob_table_tied[kmin_candidate:]),
                "prob_kmin": prob_table[kmin_candidate],
                "prob_kmin_tied": prob_table_tied[kmin_candidate],
                "delta": delta,
                "alpha": sum(prob_table_tied[kmin_candidate:])/sum(prob_table[kmin_candidate:])
            }
        else:
            return {
                "kmin": None,
                "prob_stop": 0.0,
                "prob_stop_tied": 0.0,
                "prob_kmin": None,
                "prob_kmin_tied": None,
                "delta": None,
                "alpha": None
            }


    def find_stopping_probability(self, margin, new_round_schedule, prob_table_prev):
        #round_candidate = new_round_schedule[-1]
        #if len(new_round_schedule) > 1:
        #    round_size_prev = new_round_schedule[-2]
        #else:
        #    round_size_prev = 0
        #p = (1+margin)/2


        #draws_dist = binom.pmf(range(0, (round_candidate - round_size_prev) + 1), (round_candidate - round_size_prev), p)
        #prob_table = fftconvolve(prob_table_prev, draws_dist)
        #result = self.audit(margin, new_round_schedule)
        #kmin = result["kmins"][-1]
        #stopping_probability = sum(prob_table[kmin:])
        result = self.find_next_round_kmin(margin, new_round_schedule)
        #kmin = result["kmin"]
        stopping_probability = result["prob_stop"]
        return stopping_probability


    def find_next_round_size(self, margin, round_schedule, quant, round_min, observations_i, observations_j):
        """
        For given audit parameters, computes the expected size of the next round.

        Parameters
        ----------
        :param observations:
        :param margin: margin for that race
        :param alpha: risk limit
        :param delta: delta parameter
        :param round_schedule: round schedule
        :param quant: desired probability of stopping in the next round
        :param round_min: min size of the next round
        :param observations_i: number of ballots drawn for the winner (so far) in the audit
        :param observations_j: number of ballots drawn for the loser (so far) in the audit
        :return:

            * size - the size of the next round
            * prob_stop - the probability of
        """
        #TODO: change the upper limit round_max into a parameter (or a value depending on the number of ballots cast)
        #if quant <= .9  and len(round_schedule) < 1:
        #    round_max = math.ceil((18 * math.log(self.alpha))/(margin *  (math.log(1 - margin) - math.log(1 + margin))))
        #else:
        #    round_max = 100000 # * ballots_cast
        round_max = 100000
        #upper_limit = 100000
        #round_max = upper_limit # * ballots_cast

        round_size_prev = observations_i + observations_j

        prob_table_prev = [0] * (observations_i + 1)
        prob_table_prev[observations_i] = 1.0
        new_round_schedule = round_schedule + [round_max]
        stopping_probability_max = self.find_stopping_probability(margin, new_round_schedule, prob_table_prev)

        if stopping_probability_max < quant:
            logging.warning("FULL RECOUNT is suggested! (upper_limit = %s)" % (round_max))
            logging.warning("Probability of stopping at: %s is %s" % (new_round_schedule, stopping_probability_max))
            return {"size": round_max, "prob_stop": stopping_probability_max}


        if len(round_schedule) > 0:
            round_candidate = round_schedule[-1] + math.floor((round_max)/2)
        else:
            round_candidate = math.floor((round_max)/2)

        round_min_found = False


        while round_min_found is False and round_max > 1:
            new_round_schedule = round_schedule + [round_candidate]
            stopping_probability = self.find_stopping_probability(margin, new_round_schedule, prob_table_prev)
            if stopping_probability >= quant:
                round_max = round_candidate
                if len(round_schedule) > 0:
                    round_candidate = round_schedule[-1] + math.floor((round_max - round_schedule[-1])/2)
                elif round_max > 30:
                    round_candidate = math.ceil((round_max)/2)
                else:
                    round_candidate = round_max - 1
            else:
                round_min = round_candidate
                round_min_found = True


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
            stopping_probability = self.find_stopping_probability(margin, new_round_schedule, prob_table_prev)

            if stopping_probability <= quant:
                round_min = round_candidate
            else:
                round_max = round_candidate

            # TODO: change "10" into something parametrized
            if (0 < stopping_probability - quant < .0001) or round_max - round_min <= 1:
                round_candidate = round_max
                new_round_schedule = round_schedule + [round_candidate]
                stopping_probability = self.find_stopping_probability(margin, new_round_schedule, prob_table_prev)
                break

        good_candidate = round_candidate
        good_pstop = stopping_probability #prob_table[-1]

        # we found a point for which the inequalities are met
        # but maybe we may go down a little bit... one by one:
        while True:
            round_candidate = round_candidate - 1
            new_round_schedule = round_schedule + [round_candidate]
            stopping_probability = self.find_stopping_probability(margin, new_round_schedule, prob_table_prev)

            if stopping_probability <= quant:
                break
            else:
                good_candidate = round_candidate
                good_pstop = stopping_probability


        return {"size": good_candidate, "prob_stop": good_pstop}


    def find_next_round_sizes(self, margin, round_schedule, quants, observations_i, observations_j):
        '''
        For a given list of possible stopping probabilities (called quants e.g., quants = [.7, .8, .9]) returns a list of
        next round sizes  for which probability of stoping is larger than quants

        ...

        Parameters
        ----------
        :param observations:
        :param margin: margin for given race
        :param alpha: risk limit
        :param round_schedule: round schedule (so far)
        :param quants: list of desired stopping probabilities
        :return: a list of expected round sizes
        '''
        rounds = []
        prob_stop = []
        for quant in quants:
            if len(round_schedule) > 0:
                results = self.find_next_round_size(margin, round_schedule, quant, round_schedule[-1] + 1, observations_i, observations_j)
            else:
                results = self.find_next_round_size(margin, round_schedule, quant, 1, observations_i, observations_j)

            #new_round = results["size"]
            #new_round_schedule = round_schedule + [new_round]
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
            else:
                audit_ratio[round] = 0.0




            if prob_table[kmins[round]] != 0 and round < len(audit_observations):
                if prob_table[audit_observations[round]] > 0:
                    deltas.append(abs(prob_tied_table[audit_observations[round]] / prob_table[audit_observations[round]]))
                else:
                    deltas.append(0.0)

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


class Athena(AthenaAudit):

    def __init__(self, alpha):
        AthenaAudit.__init__(self, "athena", alpha, 1.0)


class Arlo(AthenaAudit):

    def __init__(self, alpha):
        AthenaAudit.__init__(self, "arlo", alpha, alpha)


class Minerva(AthenaAudit):

    def __init__(self, alpha):
        AthenaAudit.__init__(self, "minerva", alpha, alpha)


class Metis(AthenaAudit):

    def __init__(self, alpha):
        AthenaAudit.__init__(self, "metis", alpha, alpha)
