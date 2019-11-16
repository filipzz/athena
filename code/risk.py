import sys

import numpy as np
from scipy.stats import binom

import rla as rla
import tools as tools


def __init__(self):
    pass




def calculate_risk_and_probability_b2(round_size, winner, ballots_cast, alpha, model, save_to):
    #TODO: take into account model -- now only Binary distribution (with replacement is used)
    sum = np.longdouble(0.0) #S("0")
    p_risk = .5 # S("0.5")
    p_succ = winner/ballots_cast


    #if model == "bin":
    max = rla.bravo_kmin(ballots_cast, winner, alpha, round_size)
    #else:
    #    max = rla.bravo_like_kmin(ballots_cast, winner, alpha, round_size)

    if max <= round_size:

        p_table = np.zeros(round_size + 1) #[S("0")] * (round_size)
        p_table_tmp = np.zeros(round_size + 1) #[S("0")] * (round_size)


        p_table_c = np.zeros((max + 1, round_size+1)) # [[S("0")] * (round_size)  for i in range(max)]#] * round_size
        p_table_c[0][0] = (1-p_succ)
        p_table_c[1][0] = (p_succ)

        r_table = np.zeros(round_size + 1) # [S("0")] * (round_size)
        r_table_tmp = np.zeros(round_size + 1) #[S("0")] * (round_size)


        r_table_c = np.zeros((max + 1, round_size+1)) # [[S("0")] * (round_size)  for i in range(max)]#] * round_size
        r_table_c[0][0] = (1-p_risk)
        r_table_c[1][0] = (p_risk)

        # TODO: data aggregated in p_table_cs[] are only for research purposes -- remove for real world use
        #p_table_cx = np.zeros((max, round_size)) # [[S("0")] * (round_size) for i in range(max)]
        #p_table_cx[0][0] = 1
        #p_table_cx[1][0] = 1



        for i in range(1, round_size+1):
            #if model == "bin":
            kmin = rla.bravo_kmin(ballots_cast, winner, alpha, i+1)
            #else:
            #    kmin = rla.bravo_like_kmin(ballots_cast, winner, alpha, i+1)

            p_table_c[0][i] = p_table_c[0][i-1] * (1-p_succ)
            #p_table_cx[0][i] = p_table_cx[0][i-1]
            r_table_c[0][i] = p_table_c[0][i-1] * (1-p_risk)
            for k in range(kmin):
                #print(str(i) + "\t" + str(k))
                p_table_c[k][i] = p_table_c[k][i-1] * (1-p_succ) + p_table_c[k-1][i-1] * p_succ
                r_table_c[k][i] = r_table_c[k][i-1] * (1-p_risk) + r_table_c[k-1][i-1] * p_risk
                #p_table_cx[k][i] = p_table_cx[k][i-1] + p_table_cx[k-1][i-1]



        for i in range(round_size+1):
            sum = np.longdouble(0.0) # S("0")
            sum_risk = np.longdouble(0.0) # S("0")
            for k in range(max):
                sum = sum + p_table_c[k][i]
                sum_risk = sum_risk + r_table_c[k][i]

            p_table_tmp[i] = sum
            r_table_tmp[i] = sum_risk

        sum = np.longdouble(0.0) # S("0")
        sum_risk = np.longdouble(0.0) # S("0")
        for i in range(1,round_size):
            p_table[i] = p_table_tmp[i-1] - p_table_tmp[i]

            # this is stupid but it may happen because of floating precision
            # example: python3 aurror.py -n asd -b 15038 5274 -r 30
            # p_table[23] = -5.551115123125783e-17 = p_table_tmp[22] - p_table_tmp[23] = 0.27273331278112095 - 0.272733312781121
            if p_table[i] < 0:
                p_table[i] = 0.0

            sum = sum + p_table[i]
            r_table[i] = r_table_tmp[i-1] - r_table_tmp[i]
            if r_table[i] < 0:
                r_table[i] = 0.0
            sum_risk = sum_risk + r_table[i]
            #print("p[%s] = %s = %s - %s\t\t r[%s] = %s = %s - %s" % (i, p_table[i], p_table_tmp[i-1], p_table_tmp[i], i, r_table[i], r_table_tmp[i-1], r_table_tmp[i]))

    if save_to != "false":
        try:
            tools.save_table(r_table, save_to + "/risk_table.json")
        except:
            sys.exit("Problem with writing to selected folder")

    #print(str(r_table))
    #print(str(np.sum(r_table)))

    #print("sympy: " + str(N(sum, 50)))

    #return  {"p_table_c": p_table_c, "p_table_cx" : p_table_cx, "p_table" : p_table, "sum" : sum, "r_table": r_table, "sum_risk" : sum_risk}
    return {"p_table": p_table, "r_table": r_table, "risk": np.sum(r_table)}




# finds kmin for a given round that is smaller than the goal
def next_round_risk(ballots_cast, winner, alpha, n, goal, dist, prevround_size, prvRoundKmin):
    sum = np.longdouble(0.0) #S("0")
    #ballots_half = np.longdouble(ballots_cast / 2) #S(ballots_cast) / 2

    # we first compute the risk that is used by the kmin computed in "regular" way -- according to Bravo stoppin rule
    #if dist == "bin":
    kmin = rla.bravo_kmin(ballots_cast, winner, alpha, n)
    #    X = Binomial('X', n, S.Half)
    #else:
    #    kmin = rla.bravo_like_kmin(ballots_cast, winner, alpha, n)
    #    X = Hypergeometric('X', ballots_cast, ballots_half, n)

    #TODO: take into account hypergeometric distribution
    for i in range(kmin, n+1):
        sum = sum +  binom.pmf(i, n, .5) #  density(X)[i]

    # now we will check consecutive candidates for new kmin
    # we accept new kmin if the risk is below the upper limit/goal

    i = kmin - 1
    correctRisk = 1
    while correctRisk == 1:
        nextProb = binom.pmf(i, n, .5) #density(X)[i]
        if nextProb < goal - sum:
            sum = sum + nextProb
            i = i - 1
        else:
            correctRisk = 0

    return {"sum" : sum, "kmin" : i+1}




def find_risk_bravo_bbb(ballots_cast, winner, alpha, model, round_schedule, save_to):
    # Finiding BRAVO ballot by ballot risk and stopping probabilities
    #print("find risk bravo called with: " + str(ballots_cast) + "\t" + str(winner) + "\t" + str(alpha) + "\t" + model + "\t" + str(round_schedule))
    max_number_of_rounds = len(round_schedule)
    upper_limit = round_schedule[max_number_of_rounds - 1]
    #risk_eval = calculate_bad_luck_cum_probab_table_b2_sympy(upper_limit, winner, ballots_cast, alpha, "risk", model)
    #prob_eval = calculate_bad_luck_cum_probab_table_b2_sympy(upper_limit, winner, ballots_cast, alpha, "prob", model)

    #bravo_eval = calculate_risk_and_probability_b2_mem(upper_limit, winner, ballots_cast, alpha, model)

    bravo_eval = calculate_risk_and_probability_b2(upper_limit, winner, ballots_cast, alpha, model, save_to)
    #risk_table = risk_eval["p_table"]
    risk_table = bravo_eval["r_table"]
    risk_goal = np.zeros(max_number_of_rounds) #[S("0")] * (max_number_of_rounds)
    #prob_table = prob_eval["p_table"]
    prob_table = bravo_eval["p_table"]
    prob_stop = np.zeros(max_number_of_rounds) #[S("0")] * (max_number_of_rounds)


    # in risk_goal[] we will store how much risk can be spent for each round
    #print(str(risk_table))
    for round in range(max_number_of_rounds):
        upper_limit_round = round_schedule[round]
        #print("len: " + str(len(risk_table[0:upper_limit_round])))
        risk_goal[round] = np.sum(risk_table[0:upper_limit_round])
        prob_stop[round] = (np.sum(prob_table[0:upper_limit_round]))
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


# This function estimates risk for a given audit realization.
# It computes how many tied elections would have better observations
# It computes probability of stopping
def estimate_rbr_risk(ballots_cast, winner, round_schedule, round_ks):

    # check if the round_ks are correct
    k_prev = 0
    for k in round_ks:
        if k - k_prev < 0:
            raise Exception('Incorrect k' + str(round_ks))
        k_prev = k

    # initializing variables
    max_number_of_rounds = len(round_ks)
    upper_limit = round_schedule[max_number_of_rounds - 1]
    max = round_ks[max_number_of_rounds - 1] #rla.bravo_kmin(ballots_cast, winner, alpha, upper_limit)

    table_size = max #or upper_limit
    p_table_c_rbr = np.zeros((table_size, max_number_of_rounds)) #[[S("0")] * (max_number_of_rounds)  for i in range(table_size)]
    r_table_c_rbr = np.zeros((table_size, max_number_of_rounds)) #[[S("0")] * (max_number_of_rounds)  for i in range(table_size)]

    # TODO: rename this variable into something that is less misleading
    risk_spent = np.zeros(max_number_of_rounds) # [S("0")] * max_number_of_rounds
    prob_stop = np.zeros(max_number_of_rounds) #[S("0")] * max_number_of_rounds

    risk_spent_arlo = np.zeros(max_number_of_rounds)
    prob_stop_arlo = np.zeros(max_number_of_rounds)


    # we do it for the first round first
    for i in range(round_ks[0]):
        r_table_c_rbr[i][0] = binom.pmf(i, round_schedule[0], .5)  #density(Xr).dict[i]
        p_table_c_rbr[i][0] = binom.pmf(i, round_schedule[0], winner/ballots_cast) # density(X).dict[i]

    risk_spent_so_far = np.longdouble(0.0) #  S("0")
    prob_spent_so_far = np.longdouble(0.0) #S("0")
    for i in range(round_ks[0]):
        risk_spent_so_far = risk_spent_so_far + r_table_c_rbr[i][0]
        prob_spent_so_far = prob_spent_so_far + p_table_c_rbr[i][0]

    risk_spent[0] = 1 - (risk_spent_so_far)
    prob_stop[0] = 1 - (prob_spent_so_far)

    #print("risk after first round: ", str((1- risk_spent_so_far)))




    # Now the main loop going for the following rounds
    for i in range(1, max_number_of_rounds):
        #print("\n\tSTARTING NEW ROUND " + str(i+1))

        risk_spent_so_far = np.longdouble(0.0) # S("0")
        for xi in range(round_ks[i-1]):
            risk_spent_so_far = risk_spent_so_far + r_table_c_rbr[xi][i-1]

        #print("\t risk spent up to: ", str(i), " round: ", str((1- risk_spent_so_far)))
        round_start_at = round_schedule[i-1]

        # now the part that we are sure its is gonna work - starting from k =
        #  kMin[-1] + 1
        for j in range(round_ks[i-1]):
            for k in range(j,round_ks[i]):
                r_table_c_rbr[k][i] = r_table_c_rbr[k][i] + r_table_c_rbr[j][i-1] * binom.pmf(k-j, round_schedule[i] - round_start_at, .5) #density(Xr).dict[k-j]
                p_table_c_rbr[k][i] = p_table_c_rbr[k][i] + p_table_c_rbr[j][i-1] * binom.pmf(k-j, round_schedule[i] - round_start_at, winner/ballots_cast) #density(X).dict[k-j]
                #print(str(round_schedule[i] - round_start_at), "\t", str(j), "\t", str(k), "\t",  str((p_table_c_rbr[j][i-1])), "\t")
                #print("\tp_table_c_rbr[", str(k), ", ", str(i), "] = ", str((p_table_c_rbr[k][i])))

        #print(str(i) + "\t" + str(round_ks[i-1]) + "\t" + str(round_ks[i]))



        # we compute what is the current risk spent
        risk_spent_so_far = np.longdouble(0.0) # S("0")
        prob_spent_so_far = np.longdouble(0) #S("0")
        for xi in range(round_ks[i]):
            risk_spent_so_far = risk_spent_so_far + r_table_c_rbr[xi][i]
            prob_spent_so_far = prob_spent_so_far + p_table_c_rbr[xi][i]

        risk_spent[i] = 1 - (risk_spent_so_far)
        prob_stop[i] = 1 - (prob_spent_so_far)


        #print("risk spent so far: (before last while)", str(1 - (risk_spent_so_far)))


    avg_star = 0
    prev_prob = 0.0

    for prob, round_end in zip(prob_stop, round_schedule):
        avg_star = avg_star + (prob - prev_prob) * (round_end )
        prev_prob = prob

    avg = avg_star + (1 - prev_prob) * ballots_cast




    return {"risk_spent" : risk_spent, "prob_stop" : prob_stop}


def find_kmins_for_risk(audit_kmins, actual_kmins):

    kmins_goal_real = []
    rewrite_on = 1
    for i in range(min(len(audit_kmins), len(actual_kmins))-1):
        if rewrite_on == 1:
            if audit_kmins[i] <= actual_kmins[i]:
                kmins_goal_real.append(actual_kmins[i])
                rewrite_on = 0
            else:
                kmins_goal_real.append(audit_kmins[i])

    if rewrite_on == 1:
        kmins_goal_real.append(actual_kmins[len(actual_kmins)-1])

    return kmins_goal_real
