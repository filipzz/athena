from fractions import Fraction
from sympy import S, N
from sympy.stats import Binomial, Hypergeometric, density

import numpy as np
import rla as rla


def __init__(self):
    pass


def calculate_bad_luck_cum_probab_table_b2_sympy(round_size, winner, ballots_cast, alpha, what, model):
    sum = S("0")
    if what == "risk":
        p = S("0.5")
    else:
        p = S(winner)/S(ballots_cast)


    if model == "bin":
        max = rla.bravo_kmin(ballots_cast, winner, alpha, round_size)
    else:
        max = rla.bravo_like_kmin(ballots_cast, winner, alpha, round_size)

    if max <= round_size:

        p_table = [S("0")] * (round_size)
        p_table_tmp = [S("0")] * (round_size)


        p_table_c = [[S("0")] * (round_size)  for i in range(max)]#] * round_size
        p_table_c[0][0] = (1-p)
        p_table_c[1][0] = (p)

        p_table_cx = [[S("0")] * (round_size) for i in range(max)]
        p_table_cx[0][0] = 1
        p_table_cx[1][0] = 1


        #print(">>> " + str(round_size) + "\t" + str(max))
        #print("--" + str(len(p_table)) + "\t" + str(len(p_table_c)))

        for i in range(1, round_size):
            if model == "bin":
                kmin = rla.bravo_kmin(ballots_cast, winner, alpha, i+1)
            else:
                kmin = rla.bravo_like_kmin(ballots_cast, winner, alpha, i+1)

            p_table_c[0][i] = p_table_c[0][i-1] * (1-p)
            p_table_cx[0][i] = p_table_cx[0][i-1]
            for k in range(kmin):
                #print(str(i) + "\t" + str(k))
                p_table_c[k][i] = p_table_c[k][i-1] * (1-p) + p_table_c[k-1][i-1] * p
                p_table_cx[k][i] = p_table_cx[k][i-1] + p_table_cx[k-1][i-1]


#        for k in range(0, kmin):
#            strg = ""
#            for i in range(0, round_size):
#                strg += "\t{:,.10f}".format(p_table_c[k][i])
#            print(strg + "\n")

        #for k in range(0, kmin):
        #strg = ""
        #for i in range(0, round_size):
        #strg += "\t{:,.10f}".format(float(p_table_c[9][8]))
        #print(strg + "\n")

        for i in range(round_size):
            sum = 0
            for k in range(max):
                sum = sum + p_table_c[k][i]

            p_table_tmp[i] = sum

        sum = np.longdouble(0)
        for i in range(1,round_size):
            p_table[i] = p_table_tmp[i-1] - p_table_tmp[i]
            sum = sum + p_table[i]

    #print("sympy: " + str(N(sum, 50)))

    return  {"p_table_c": p_table_c, "p_table_cx" : p_table_cx, "p_table" : p_table, "sum" : sum}


# finds kmin for a given round that is smaller than the goal
def next_round_risk(ballots_cast, winner, alpha, n, goal, dist, prevround_size, prvRoundKmin):
    sum = S("0")
    ballots_half = S(ballots_cast) / 2

    # we first compute the risk that is used by the kmin computed in "regular" way -- according to Bravo stoppin rule
    if dist == "bin":
        kmin = rla.bravo_kmin(ballots_cast, winner, alpha, n)
        X = Binomial('X', n, S.Half)
    else:
        kmin = rla.bravo_like_kmin(ballots_cast, winner, alpha, n)
        X = Hypergeometric('X', ballots_cast, ballots_half, n)

    for i in range(kmin, n+1):
        sum = sum + density(X)[i]

    # now we will check consecutive candidates for new kmin
    # we accept new kmin if the risk is below the upper limit/goal

    i = kmin - 1
    correctRisk = 1
    while correctRisk == 1:
        nextProb = density(X)[i]
        if nextProb < goal - sum:
            sum = sum + nextProb
            i = i - 1
        else:
            correctRisk = 0

    return {"sum" : sum, "kmin" : i+1}




def find_risk_bravo_bbb(ballots_cast, winner, alpha, model, round_schedule):
    # Finiding BRAVO ballot by ballot risk and stopping probabilities
    #print("find risk bravo called with: " + str(ballots_cast) + "\t" + str(winner) + "\t" + str(alpha) + "\t" + model + "\t" + str(round_schedule))
    max_number_of_rounds = len(round_schedule)
    upper_limit = round_schedule[max_number_of_rounds - 1]
    risk_eval = calculate_bad_luck_cum_probab_table_b2_sympy(upper_limit, winner, ballots_cast, alpha, "risk", model)
    prob_eval = calculate_bad_luck_cum_probab_table_b2_sympy(upper_limit, winner, ballots_cast, alpha, "prob", model)

    risk_table = risk_eval["p_table"]
    risk_goal = [S("0")] * (max_number_of_rounds)
    prob_table = prob_eval["p_table"]
    prob_stop = [S("0")] * (max_number_of_rounds)


    # in risk_goal[] we will store how much risk can be spent for each round
    for round in range(max_number_of_rounds):
        upper_limit_round = round_schedule[round]
        risk_goal[round] = sum(risk_table[0:upper_limit_round])
        prob_stop[round] = N(sum(prob_table[0:upper_limit_round]))
        #print(str(round+1) + "\t" + str(round_schedule[round]) + "\t" + str(risk_goal[round]) + "\t" + str(upper_limit))

    bravo_kmins = map(lambda n: rla.bravo_kmin(ballots_cast, winner, alpha, n), round_schedule )
    kmins = []
    for km in bravo_kmins:
        kmins.append(km)

    return {"risk_goal" : risk_goal, "prob_stop" : prob_stop, "kmins" : kmins}


#
#
# next functions are for comparison only: they use different number formats floats/numpy/fraction
#
#

def calculate_bad_luck_cum_probab_table_b2(round_size, winner, ballots_cast, alpha, what, model):
    sum = 0
    ballots_half = np.floor(ballots_cast/2)
    wnR = np.floor(ballots_cast/2)
    pNotFinishedYet = 1
    if what == "risk":
        p = 1/2
        q = 1 - p
    else:
        p = winner/ballots_cast
        q = 1 - p


    if model == "bin":
        max = rla.bravo_kmin(ballots_cast, winner, alpha, round_size)
    else:
        max = rla.bravo_like_kmin(ballots_cast, winner, alpha, round_size)

    if max <= round_size:

        p_table = [0] * (round_size)
        p_table_tmp = [0] * (round_size)

        #print(p_table_tmp)

        p_table_c = [[0] * (round_size)  for i in range(max)]#] * round_size
        p_table_c[0][0] = 1-p
        p_table_c[1][0] = p


        #print(">>> " + str(round_size) + "\t" + str(max))
        #print("--" + str(len(p_table)) + "\t" + str(len(p_table_c)))

        for i in range(1, round_size):
            if model == "bin":
                kmin = rla.bravo_kmin(ballots_cast, winner, alpha, i+1)
            else:
                kmin = rla.bravo_like_kmin(ballots_cast, winner, alpha, i+1)

            p_table_c[0][i] = p_table_c[0][i-1] * (1-p)
            for k in range(kmin):
                #print(str(i) + "\t" + str(k))
                p_table_c[k][i] = p_table_c[k][i-1] * (1-p) + p_table_c[k-1][i-1] * p


        #for k in range(0, kmin):
        #strg = ""
        #for i in range(0, round_size):
        #strg += "\t{:,.10f}".format(float(p_table_c[9][8]))
        #print(strg + "\n")


        for i in range(round_size):
            sum = 0
            for k in range(max):
                sum = sum + p_table_c[k][i]

            p_table_tmp[i] = sum

        sum = 0
        for i in range(1,round_size):
            p_table[i] = p_table_tmp[i-1] - p_table_tmp[i]
            sum += p_table[i]

    print("float: " + str(sum))

    return  { "p_table" : p_table, "sum" : sum}

def calculate_bad_luck_cum_probab_table_b2_longdouble(round_size, winner, ballots_cast, alpha, what, model):
    sum = 0
    ballots_half = np.floor(np.longdouble(ballots_cast)/2)
    wnR = np.floor(np.longdouble(ballots_cast)/2)
    pNotFinishedYet = 1
    if what == "risk":
        p = np.longdouble(1/2)
        q = np.longdouble(1 - p)
    else:
        p = np.longdouble(winner/ballots_cast)
        q = 1 - p


    if model == "bin":
        max = rla.bravo_kmin(ballots_cast, winner, alpha, round_size)
    else:
        max = rla.bravo_like_kmin(ballots_cast, winner, alpha, round_size)

    if max <= round_size:

        p_table = [np.longdouble(0)] * (round_size)
        p_table_tmp = [np.longdouble(0)] * (round_size)


        p_table_c = [[np.longdouble(0)] * (round_size)  for i in range(max)]#] * round_size
        p_table_c[0][0] = np.longdouble(1-p)
        p_table_c[1][0] = np.longdouble(p)


        for i in range(1, round_size):
            if model == "bin":
                kmin = rla.bravo_kmin(ballots_cast, winner, alpha, i+1)
            else:
                kmin = rla.bravo_like_kmin(ballots_cast, winner, alpha, i+1)

            p_table_c[0][i] = p_table_c[0][i-1] * (1-p)
            for k in range(kmin):
                #print(str(i) + "\t" + str(k))
                p_table_c[k][i] = p_table_c[k][i-1] * (1-p) + p_table_c[k-1][i-1] * p



        for i in range(round_size):
            sum = 0
            for k in range(max):
                sum = sum + p_table_c[k][i]

            p_table_tmp[i] = sum

        sum = np.longdouble(0)
        for i in range(1,round_size):
            p_table[i] = p_table_tmp[i-1] - p_table_tmp[i]
            sum = sum + p_table[i]

    print("numpy: " + str(sum))

    return  { "p_table" : p_table, "sum" : sum}




def calculate_bad_luck_cum_probab_table_b2_frac(round_size, winner, ballots_cast, alpha, what, model):
    sum = 0
    ballots_half = Fraction(ballots_cast,2)
    wnR = Fraction(ballots_cast,2)
    pNotFinishedYet = 1
    if what == "risk":
        p = Fraction(1, 2)
        q = 1 - p
    else:
        p = Fraction(winner, ballots_cast)
        q = 1 - p


    if model == "bin":
        max = rla.bravo_kmin(ballots_cast, winner, alpha, round_size)
    else:
        max = rla.bravo_like_kmin(ballots_cast, winner, alpha, round_size)

    if max <= round_size:

        p_table = [0] * (round_size)
        p_table_tmp = [Fraction(0,1)] * (round_size)

        #print(p_table_tmp)

        p_table_c = [[Fraction(0,1)] * (round_size)  for i in range(max)]#] * round_size
        p_table_c[0][0] = 1-p
        p_table_c[1][0] = p


        #print(">>> " + str(round_size) + "\t" + str(max))
        #print("--" + str(len(p_table)) + "\t" + str(len(p_table_c)))

        for i in range(1, round_size):
            if model == "bin":
                kmin = rla.bravo_kmin(ballots_cast, winner, alpha, i+1)
            else:
                kmin = rla.bravo_like_kmin(ballots_cast, winner, alpha, i+1)

            p_table_c[0][i] = p_table_c[0][i-1] * (1-p)
            for k in range(kmin):
                #print(str(i) + "\t" + str(k))
                p_table_c[k][i] = p_table_c[k][i-1] * (1-p) + p_table_c[k-1][i-1] * p


        #for k in range(0, kmin):
        #strg = ""
        #for i in range(0, round_size):
        #strg += "\t{:,.10f}".format(float(p_table_c[9][8]))
        #print(strg + "\n")


        for i in range(round_size):
            sum = 0
            for k in range(max):
                sum = sum + p_table_c[k][i]

            p_table_tmp[i] = sum

        sum = 0
        for i in range(1,round_size):
            p_table[i] = p_table_tmp[i-1] - p_table_tmp[i]
            sum = sum + p_table[i]

    print("frac:  " + str(float(sum)))

    return  {"p_table" : p_table, "sum" : sum}
