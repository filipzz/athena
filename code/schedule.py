import rla as rla
import risk as risk
from sympy import S, N
from sympy.stats import Binomial, Hypergeometric, density
import math


def __init__():
    pass

def print_iterator(it):
    strg = []
    for x in it:
        strg.append(x)
    return strg  # for new line

def print_election_info(ballots_cast, winner, margin, alpha, model):
    print("Number of valid ballots: " + str(ballots_cast))
    print("(Declared) Votes for winner: " + str(winner))
    print("Margin: " + str(margin))
    print("Alpha:  " + str(alpha))
    print("Model:  " + str(model))


def main():

    # Setting up the parameters for the audit
    margin = .2
    ballots_cast = 1000
    winner = math.floor((1+margin)/2* ballots_cast)
    round_schedule = [19, 50, 120]#[301, 518, 916]#, 1520, 3366]
    alpha = .1
    what = "risk"
    model = "bin"
    max_number_of_rounds = len(round_schedule)
    upper_limit = round_schedule[max_number_of_rounds - 1]

    print_election_info(ballots_cast, winner, margin, alpha, model)

    # Printing
    print("Proposed round sizes: " + str(round_schedule))
    #bravo_kmins = map(lambda n: rla.bravo_kmin(ballots_cast, winner, alpha, n), round_schedule )
    #print("\tBRAVO kmins: " + str(print_iterator(bravo_kmins)))


    # this is time-consuming part -- you can use precomputed values if you have the same
    #
    bravo_parameters = risk.find_risk_bravo_bbb(ballots_cast, winner, alpha, model, round_schedule)
    risk_goal = bravo_parameters["risk_goal"]
    prob_stop_bravo = bravo_parameters["prob_stop"]
    kmins_bravo = bravo_parameters["kmins"]


    print("\tBRAVO risk: " + str(risk_goal))
    print("\tBRAVO pstop: " + str(prob_stop_bravo))
    print("\tBRAVO kmins: " + str(kmins_bravo))

    #print("Risk goal: " + str(risk_goal))
    # initializing variables
    pTableRbR = [S("0")] * (max_number_of_rounds)
    max = rla.bravo_kmin(ballots_cast, winner, alpha, upper_limit)
    p_table_c_rbr = [[S("0")] * (max_number_of_rounds)  for i in range(max)]
    risk_spent = [S("0")] * max_number_of_rounds
    prob_stop = [S("0")] * max_number_of_rounds




    # finding round numbers:
    # - kmin
    # - probability of stopping

    # first round is "special"
    # TODO: make the fist round the part of the main loop

    nrr = risk.next_round_risk(ballots_cast, winner, alpha, round_schedule[0], risk_goal[0], "bin", 0, 0)

    kmin_prime = nrr["kmin"]
    kmin_new = [kmin_prime] * max_number_of_rounds

    #print(str((nrr["sum"])))

    #print(str(nrr["kmin"]))


    # we do it for the first round first
    # TODO: we need to add hypergeometric (after we figure out how to deal with invalid votes)
    for i in range(kmin_prime):
        X = Binomial('X', round_schedule[0], S.Half)
        p_table_c_rbr[i][0] = density(X).dict[i]
        #print(str(i) + "\t" + str(N(density(X).dict[i])))

    risk_spent_so_far = S("0")
    for i in range(kmin_prime):
        risk_spent_so_far = risk_spent_so_far + p_table_c_rbr[i][0]


    risk_spent[0] = 1 - N(risk_spent_so_far)

    # print("risk after first round: ", str(N(1- risk_spent_so_far)))




    # Now the main loop going for the following rounds
    for i in range(1, max_number_of_rounds):
        print("\n\tSTARTING NEW ROUND " + str(i+1))

        risk_spent_so_far = S("0")
        for xi in range(kmin_new[i-1]):
            risk_spent_so_far = risk_spent_so_far + p_table_c_rbr[xi][i-1]

        print("\trisk spent up to: ", str(i), " round: ", str(N(1- risk_spent_so_far)))
        round_start_at = round_schedule[i-1]

        # now the part that we are sure its is gonna work - starting from k =
        #  kMin[-1] + 1
        for j in range(kmin_new[i-1]):
            for k in range(j,kmin_new[i-1]):
                X = Binomial('X', round_schedule[i] - round_start_at, S.Half)
                p_table_c_rbr[k][i] = p_table_c_rbr[k][i] + p_table_c_rbr[j][i-1] * density(X).dict[k-j]
                #print(str(round_schedule[i] - round_start_at), "\t", str(j), "\t", str(k), "\t",  str(N(p_table_c_rbr[j][i-1])), "\t", str(N(density(X).dict[k-j])) )
                #print("p_table_c_rbr[", str(k), ", ", str(i), "] = ", str(N(p_table_c_rbr[k][i])))

        #print(str(i) + "\t" + str(kmin_new[i-1]))

        #print(kmin_prime)


        # we compute what is the current risk spent
        risk_spent_so_far = S("0")
        for xi in range(kmin_new[i-1]):
            risk_spent_so_far = risk_spent_so_far + p_table_c_rbr[xi][i]

        #print("risk spent so far: (before last while)", str(1 - N(risk_spent_so_far)))

        correct_risk_level = 1

        # now we need to find what is kmin_prime for the current round -
        #  we will try to add new, larger values of k,
        # as long as the risk_goal is not exceeded

        k = kmin_new[i-1]

        #print(">>" + str(kmin_new[i-1]) + "\t" + str(round_schedule[i] - round_start_at))
        while correct_risk_level == 1:
            for j in range(min(kmin_new[i-1], round_schedule[i] - round_start_at)):
                X = Binomial('X', round_schedule[i] - round_start_at, S.Half)
                if k - j <= round_schedule[i] - round_start_at:
                    p_table_c_rbr[k][i] = p_table_c_rbr[k][i] + p_table_c_rbr[j][i-1] * density(X).dict[k-j]
                    #print(str(round_schedule[i] - round_start_at), "\t", str(j), "\t", str(k), "\t",  str(N(p_table_c_rbr[j][i-1])), "\t", str(N(density(X).dict[k-j])) )
                #print("p_table_c_rbr[", str(k), ", ", str(i), "] = ", str(N(p_table_c_rbr[k][i])))


            risk_spent_so_far = S("0")
            for xi in range(k+1):
                risk_spent_so_far = risk_spent_so_far + p_table_c_rbr[xi][i]

            #print(str(i) + "\t" + str(k) + "\t" + str(N(risk_spent_so_far)))

            risk_spent[i] = 1 - N(risk_spent_so_far)


            if (1 - N(risk_spent_so_far)) < N(risk_goal[i]):
                kmin_new[i] = k + 1
                correct_risk_level = 0
                #print("new kmin_new: " + str(kmin_new[i]))

            k = k + 1



    print("\n\tAURROR kmins:\t\t" + str(kmin_new))

    print("\tAURROR risk: " + str(risk_spent))










if __name__ == '__main__':
    main()
