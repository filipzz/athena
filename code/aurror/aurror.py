from scipy.stats import binom
import math

class AurrorAudit():
    def next_round_prob(self, margin, round_size_prev, round_size, kmin, prob_table_prev):
        prob_table = [0] * (round_size + 1)
        for i in range(kmin + 1):
            for j in range(round_size + 1):
                prob_table[j] = prob_table[j] + binom.pmf(j-i, round_size - round_size_prev, (1+margin)/2) * prob_table_prev[i]

        return prob_table

    def aurror(self, margin, alpha, round_schedule):
        round_schedule = [0] + round_schedule
        number_of_rounds = len(round_schedule)
        prob_table_prev = [1]
        prob_tied_table_prev = [1]
        kmins = [0] * number_of_rounds
        prob_sum = [0] * number_of_rounds
        prob_tied_sum = [0] * number_of_rounds

        for round in range(1,number_of_rounds):
            prob_table = self.next_round_prob(margin, round_schedule[round - 1], round_schedule[round], kmins[round - 1], prob_table_prev)
            prob_tied_table = self.next_round_prob(0, round_schedule[round - 1], round_schedule[round], kmins[round - 1], prob_tied_table_prev)

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

    '''
        Given audit parameters: **margin**, **alpha**, and  **round_schedule** so far, for a given **quant**
        the size of the next round will be found.
    '''
    def find_next_round_size(self, margin, alpha, round_schedule, quant, round_min):

        if len(round_schedule) > 0:
            round_candidate = 2 * round_schedule[-1]
            round_min = round_schedule[-1]
            #round_max = round_candidate
        else:
            round_candidate = round_min
            #round_max = 2 * round_candidate

        # TODO: make sure that round_min leads to the situation where audit with a given round schedule extended with round_min stops with probability less than quant

        #print("\tfnrs:\t" + str(quant) + "\t" + str(round_min) + "\t" + str(round_candidate))

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

        return {"size" : round_candidate, "prob_stop" : prob_table[-1]}

    '''
        For a given list of quants (e.g., quants = [.7, .8, .9] returns a list of
        next round sizes  for which probability of stoping is larger than quants
    '''
    def find_next_round_sizes(self, margin, alpha, round_schedule, quants):
        round_candidate = 100
        for quant in quants:
            results = self.find_next_round_size(margin, alpha, round_schedule, quant, round_candidate)
            new_round = results["size"]
            new_round_schedule = round_schedule + [new_round]
            print("\t" + str(quant) + "\t" + str(new_round_schedule))
            round_candidate = results["size"]

    def relative_prob(self, prob_table):
        if len(prob_table) == 1:
            return prob_table[-1]
        else:
            prob_prev = prob_table[-2]
            prob_last = prob_table[-1]
            prob_total = 1 - prob_prev
            prob_gain = prob_last - prob_prev
            return prob_gain / prob_total
