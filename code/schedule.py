import rla as rla
import risk as risk
#from sympy import S, N
from sympy.stats import Binomial, Hypergeometric, density
import numpy as np
from scipy.stats import binom
import math

import tools as tools




def find_new_kmins_max_risk(ballots_cast, winner, alpha, round_schedule, risk_goal):
    # in this version, we change the risk_goal for the last round by replacing it with alpha
    modified_risk_goal = risk_goal
    modified_risk_goal[len(risk_goal)-1] = alpha
    return find_new_kmins(ballots_cast, winner, alpha, round_schedule, modified_risk_goal)


def find_new_kmins(ballots_cast, winner, alpha, round_schedule, risk_goal):

    #print("find_new_kmins(%s, %s, %s, %s, %s)" % (ballots_cast, winner, alpha, round_schedule, risk_goal))

    # check if the risk goal is correct (it needs to be increasing with elements smaller than alpha)
    r_prev = 0
    for r in risk_goal:
        if r - r_prev < 0 or r > alpha:
            raise Exception('Incorrect risk_goal')
        r_prev = r

        #print("Risk goal: " + str(risk_goal))
    # initializing variables
    max_number_of_rounds = len(round_schedule)
    upper_limit = round_schedule[max_number_of_rounds - 1]
    #pTableRbR = [S("0")] * (max_number_of_rounds)
    max = rla.bravo_kmin(ballots_cast, winner, alpha, upper_limit)
    #p_table_c_rbr = [[S("0")] * (max_number_of_rounds)  for i in range(max)]
    #r_table_c_rbr = [[S("0")] * (max_number_of_rounds)  for i in range(max)]
    #TODO: table_size = max/upper_limit - for "reasonable" risk_goal (e.g., following bravo risk schedule) table_size = max will be smaller than bravo_kmin
    table_size = max #or upper_limit
    p_table_c_rbr = np.zeros((table_size, max_number_of_rounds)) #[[S("0")] * (max_number_of_rounds)  for i in range(table_size)]
    r_table_c_rbr = np.zeros((table_size, max_number_of_rounds)) #[[S("0")] * (max_number_of_rounds)  for i in range(table_size)]

    # TODO: rename this variable into something that is less misleading
    risk_spent = np.zeros(max_number_of_rounds) # [S("0")] * max_number_of_rounds
    prob_stop = np.zeros(max_number_of_rounds) #[S("0")] * max_number_of_rounds

    risk_spent_arlo = np.zeros(max_number_of_rounds)
    prob_stop_arlo = np.zeros(max_number_of_rounds)




    # finding round numbers:
    # - kmin
    # - probability of stopping

    # first round is "special"
    # TODO: make the fist round the part of the main loop

    nrr = risk.next_round_risk(ballots_cast, winner, alpha, round_schedule[0], risk_goal[0], "bin", 0, 0)

    kmin_prime = nrr["kmin"]
    kmin_new = [kmin_prime] * max_number_of_rounds
    #for i, rsx in zip(range(len(round_schedule)), round_schedule):
    #    print("\t" + str(i) + "\t" + str(rsx) + "\t" + str(rla.bravo_kmin(ballots_cast, winner, alpha, round_schedule[i])))
        #kmin_new[i] = rla.bravo_kmin(ballots_cast, winner, alpha, round_schedule[i])
        #kmin_new[i] = rla.bravo_kmin(ballots_cast, winner, alpha, round_schedule[i])
    #print(str((nrr["sum"])))

    #print(str(nrr["kmin"]))


    #
    #
    # arlo start
    # this is part for calculating arlo parameters only:
    bravo_kmin = rla.bravo_kmin(ballots_cast, winner, alpha, round_schedule[0])
    #for i in range(bravo_kmin):
    for i in range(kmin_prime):
        r_table_c_rbr[i][0] = binom.pmf(i, round_schedule[0], .5)  #density(Xr).dict[i]
        p_table_c_rbr[i][0] = binom.pmf(i, round_schedule[0], winner/ballots_cast) # density(X).dict[i]

    risk_spent_so_far = np.longdouble(0.0) #  S("0")
    prob_spent_so_far = np.longdouble(0.0) #S("0")
    for i in range(kmin_prime):
        risk_spent_so_far = risk_spent_so_far + r_table_c_rbr[i][0]
        prob_spent_so_far = prob_spent_so_far + p_table_c_rbr[i][0]


    risk_spent_arlo[0] = 1 - (risk_spent_so_far)
    prob_stop_arlo[0] = 1 - (prob_spent_so_far)

    # TODO: add similar calculations for the following rounds
    # arlo end
    #
    #


    # we do it for the first round first
    # TODO: we need to add hypergeometric (after we figure out how to deal with invalid votes)
    for i in range(kmin_prime):
        #Xr = Binomial('Xr', round_schedule[0], S.Half)
        r_table_c_rbr[i][0] = binom.pmf(i, round_schedule[0], .5)  #density(Xr).dict[i]
        #X = Binomial('X', round_schedule[0], S(winner)/S(ballots_cast))
        p_table_c_rbr[i][0] = binom.pmf(i, round_schedule[0], winner/ballots_cast) # density(X).dict[i]
        #print(str(i) + "\t" + str(N(density(X).dict[i])))

    risk_spent_so_far = np.longdouble(0.0) #  S("0")
    prob_spent_so_far = np.longdouble(0.0) #S("0")
    for i in range(kmin_prime):
        risk_spent_so_far = risk_spent_so_far + r_table_c_rbr[i][0]
        prob_spent_so_far = prob_spent_so_far + p_table_c_rbr[i][0]


    risk_spent[0] = 1 - (risk_spent_so_far)
    prob_stop[0] = 1 - (prob_spent_so_far)

    #print(str(kmin_new[0]))
    #print("risk after first round: ", str((1- risk_spent_so_far)))




    # Now the main loop going for the following rounds
    for i in range(1, max_number_of_rounds):
        #print("\n\tSTARTING NEW ROUND " + str(i+1))

        risk_spent_so_far = np.longdouble(0.0) # S("0")
        for xi in range(kmin_new[i-1]):
            risk_spent_so_far = risk_spent_so_far + r_table_c_rbr[xi][i-1]

        #print("\t risk spent up to: ", str(i), " round: ", str((1- risk_spent_so_far)))
        round_start_at = round_schedule[i-1]

        # now the part that we are sure its is gonna work - starting from k =
        #  kMin[-1] + 1
        for j in range(kmin_new[i-1]):
            for k in range(j,kmin_new[i-1]):
                #Xr = Binomial('Xr', round_schedule[i] - round_start_at, S.Half)
                r_table_c_rbr[k][i] = r_table_c_rbr[k][i] + r_table_c_rbr[j][i-1] * binom.pmf(k-j, round_schedule[i] - round_start_at, .5) #density(Xr).dict[k-j]
                #X = Binomial('X', round_schedule[i] - round_start_at, S(winner)/S(ballots_cast))
                p_table_c_rbr[k][i] = p_table_c_rbr[k][i] + p_table_c_rbr[j][i-1] * binom.pmf(k-j, round_schedule[i] - round_start_at, winner/ballots_cast) #density(X).dict[k-j]
                #print(str(round_schedule[i] - round_start_at), "\t", str(j), "\t", str(k), "\t",  str((p_table_c_rbr[j][i-1])), "\t", str((density(X).dict[k-j])) )
                #print("p_table_c_rbr[", str(k), ", ", str(i), "] = ", str((p_table_c_rbr[k][i])))

        #print(str(i) + "\t" + str(kmin_new[i-1]))

        #print(kmin_prime)


        # we compute what is the current risk spent
        risk_spent_so_far = np.longdouble(0.0) # S("0")
        for xi in range(kmin_new[i-1]):
            risk_spent_so_far = risk_spent_so_far + r_table_c_rbr[xi][i]

        #print(str(kmin_new[i]))
        #print("risk spent so far: (before last while)", str(1 - (risk_spent_so_far)))


        correct_risk_level = 1

        # now we need to find what is kmin_prime for the current round -
        #  we will try to add new, larger values of k,
        # as long as the risk_goal is not exceeded

        k = kmin_new[i-1]

        #print(">>" + str(kmin_new[i-1]) + "\t" + str(round_schedule[i] - round_start_at))
        while correct_risk_level == 1:
            #for j in range(min(kmin_new[i-1], round_schedule[i] - round_start_at)):
            #print("j in range(min(" + str(k+1) + ", " + str(round_schedule[i] - round_start_at) + ")")
            for j in range((k + 1)):#, round_schedule[i] - round_start_at)):
                #Xr = Binomial('Xr', round_schedule[i] - round_start_at, S.Half)
                #X = Binomial('X', round_schedule[i] - round_start_at, S(winner)/S(ballots_cast))
                if k - j <= round_schedule[i] - round_start_at:
                    r_table_c_rbr[k][i] = r_table_c_rbr[k][i] + r_table_c_rbr[j][i-1] * binom.pmf(k-j, round_schedule[i] - round_start_at, .5) # density(Xr).dict[k-j]
                    p_table_c_rbr[k][i] = p_table_c_rbr[k][i] + p_table_c_rbr[j][i-1] * binom.pmf(k-j, round_schedule[i] - round_start_at, winner/ballots_cast) #density(X).dict[k-j]
                    #print(str(round_schedule[i] - round_start_at), "\t", str(j), "\t", str(k), "\t",  str(N(p_table_c_rbr[j][i-1])), "\t", str(N(density(X).dict[k-j])) )
                #print("p_table_c_rbr[", str(k), ", ", str(i), "] = ", str(N(p_table_c_rbr[k][i])))


            risk_spent_so_far = np.longdouble(0) #S("0")
            prob_spent_so_far = np.longdouble(0) #S("0")
            for xi in range(k+1):
                risk_spent_so_far = risk_spent_so_far + r_table_c_rbr[xi][i]
                prob_spent_so_far = prob_spent_so_far + p_table_c_rbr[xi][i]

            #print(str(i) + "\t" + str(k) + "\t" + str(N(risk_spent_so_far)))

            risk_spent[i] = 1 - (risk_spent_so_far)
            prob_stop[i] = 1 - (prob_spent_so_far)

            #print("testing for: " + str(k) + " - " +  str(j) + "\t" + str((1 - risk_spent_so_far)) + " <? " + str(risk_goal[i]))

            if (1 - (risk_spent_so_far)) < (risk_goal[i]):
                kmin_new[i] = k + 1
                correct_risk_level = 0
                #print("new kmin_new: " + str(kmin_new[i]))

            k = k + 1

            if k >= table_size:
                correct_risk_level = 0

    avg_star = 0
    prev_prob = 0.0

    for prob, round_end in zip(prob_stop, round_schedule):
        avg_star = avg_star + (prob - prev_prob) * (round_end )
        prev_prob = prob

    avg = avg_star + (1 - prev_prob) * ballots_cast




    return {"kmin_new" : kmin_new, "risk_spent" : risk_spent, "prob_stop" : prob_stop, "avg_star" : avg_star, "avg" : avg, "risk_spent_arlo" : risk_spent_arlo, "prob_stop_arlo" : prob_stop_arlo}



def find_aurror_params_from_schedule_and_risk(ballots_cast, winner, alpha, model, round_schedule, risk_goal, verbosity):
    aurror = find_new_kmins(ballots_cast, winner, alpha,  round_schedule, risk_goal)

    kmin_new = aurror["kmin_new"]
    risk_spent = aurror["risk_spent"]
    prob_stop = aurror["prob_stop"]

    risk_spent_arlo = aurror["risk_spent_arlo"]
    prob_stop_arlo = aurror["prob_stop_arlo"]


    #risk.estimate_rbr_risk(ballots_cast, winner,  round_schedule, kmins_goal_real)
    if verbosity > 0:
        print("\n\tARLO risk " + str(risk_spent_arlo))
        print("\tARLO pstop: " + str(prob_stop_arlo))

        print("\n\tAURROR kmins:\t\t" + str(kmin_new))

        print("\tAURROR risk: " + str(risk_spent))

        print("\tAURROR pstop: " + str(prob_stop))
        print("\t\tAVG:\t" + str(aurror["avg"]))
        print("\t\tAVG*:\t" + str(aurror["avg_star"]))

    return {"kmin_new" : kmin_new, "risk_spent": risk_spent, "prob_stop": prob_stop, "avg" : aurror["avg"], "avg_star": aurror["avg_star"]}




def find_aurror_params_from_schedule(ballots_cast, winner, alpha, model, round_schedule, pstop_goal, save_to,
                                     verbosity):

    # 1. we need to find Bravo risk for the schedule


    # this is time-consuming part -- you can use precomputed values if you have the same
    #
    bravo_parameters = risk.find_risk_bravo_bbb(ballots_cast, winner, alpha, model, round_schedule, save_to)
    risk_goal = bravo_parameters["risk_goal"]
    prob_stop_bravo = bravo_parameters["prob_stop"]
    kmins_bravo = bravo_parameters["kmins"]

    # TODO: save computed data (even earlier -- to have raw values for recomputation/change of round sizes)
    #tools.save_table(risk_goal, "1-risk_table.json")
    #tools.save_table(prob_stop_bravo, "1-prob_stop_bravo.json")
    #tools.save_table(kmins_bravo, "1-kmins_bravo.json")

    avg_star = 0
    prev_prob = 0.0

    for prob, round_end in zip(prob_stop_bravo, round_schedule):
        avg_star = avg_star + (prob - prev_prob) * (round_end )
        prev_prob = prob

    avg = avg_star + (1 - prev_prob) * ballots_cast

    if verbosity > 0:
        print("\n\tBRAVO kmins: \t" + str(kmins_bravo))
        print("\tBRAVO risk: \t" + str(risk_goal))
        print("\tBRAVO pstop: \t" + str(prob_stop_bravo))
        print("\t--- ratio:\t" + str(risk_goal / prob_stop_bravo))
        print("\t\tAVG:\t" + str(avg))
        print("\t\tAVG*:\t" + str(avg_star))


    arlo = risk.estimate_rbr_risk(ballots_cast, winner, round_schedule, kmins_bravo)
    risk_spent_arlo = arlo["risk_spent"]
    prob_stop_arlo = arlo["prob_stop"]

    if verbosity > 0:
        print("\n\tARLO kmins:\t" + str(kmins_bravo))
        print("\tARLO risk:\t" + str(risk_spent_arlo))
        print("\tARLO pstop:\t" + str(prob_stop_arlo))
        print("\t--- ratio:\t" + str(risk_spent_arlo / prob_stop_arlo))



    # 2. We use risk_goal to find new kmins
    aurror = find_new_kmins(ballots_cast, winner, alpha,  round_schedule, risk_goal)

    kmin_new = aurror["kmin_new"]
    risk_spent = aurror["risk_spent"]
    prob_stop = aurror["prob_stop"]


    risk_spent_arlo = aurror["risk_spent_arlo"]
    prob_stop_arlo = aurror["prob_stop_arlo"]

    '''
    if verbosity > 0:


        print("\n\tR2B2 kmins:\t" + str(kmin_new))
        print("\tR2B2 risk:\t" + str(risk_spent))
        print("\tR2B2 pstop:\t" + str(prob_stop))
        print("\t--- ratio:\t" + str(risk_spent / prob_stop))
        print("\t\tAVG:\t" + str(aurror["avg"]))
        print("\t\tAVG*:\t" + str(aurror["avg_star"]))
    '''
    return {"kmin_new" : kmin_new, "risk_spent": risk_spent, "prob_stop": prob_stop, "avg" : aurror["avg"], "avg_star": aurror["avg_star"], "bravo": bravo_parameters}

'''
    This version of finding kmins is different:
    - each round is treated separately, as other rounds would not exist at all (same is in Bravo)
    We lose efficiency -- we cannot lower kmins that much
    But we get rid of disambibuity
'''
def find_aurror_proper_params_from_schedule(ballots_cast, winner, alpha, model, round_schedule, pstop_goal, save_to,
                                     verbosity):
    kmin_new = []
    for round_size in round_schedule:
        result = find_aurror_params_from_schedule(ballots_cast, winner, alpha, model, [round_size], [], save_to, 0)
        kmin_new.append(result["kmin_new"][0])

    #print(str(kmin_new))

    audit = risk.estimate_rbr_risk(ballots_cast, winner, round_schedule, kmin_new)
    risk_spent = audit["risk_spent"]
    prob_stop = audit["prob_stop"]

    if verbosity > 0:
        print("\n\tAurror kmins:\t" + str(kmin_new))
        print("\tAurror risk:\t" + str(risk_spent))
        print("\tAurror pstop:\t" + str(prob_stop))
        print("\t--- ratio:\t" + str(risk_spent / prob_stop))


    return {"kmin_new" : kmin_new, "risk_spent": risk_spent, "prob_stop": prob_stop}


if __name__ == '__main__':
        # Setting up the parameters for the audit
    margin = .1
    ballots_cast = 14000 #20227
    winner = math.floor((1+margin)/2* ballots_cast)
    winner = 7700 #14970
    ballots_cast = 15038 + 5274
    winner = 15038
    round_schedule = [41]#, 600]#, 332, 587, 974, 2155]#[301, 518, 916]#, 1520, 3366]
    round_schedule = [ 193, 332, 587, 974, 2155]
    round_schedule = [34, 57]
    alpha = .1
    model = "bin"

    #print_election_info(ballots_cast, winner, margin, alpha, model)

    print("Round schedule: " + str(round_schedule))
    # Calling: find_aurror_params_from_schedule(...)
    # 1. finds parameters for BRAVO
    # 2. finds parameters for Aurror
    #find_aurror_params_from_schedule(ballots_cast, winner, alpha, model, round_schedule, "false")
    r = find_aurror_params_from_schedule(ballots_cast, winner, alpha, model, round_schedule, [], "false", 1)
    #print(str(r))
    # Calling: find_aurror_params_from_schedule_and_risk(...)
    # just finds parameters for Aurror
    #risk_goal = [alpha] * len(round_schedule)#, .0999999]
    #risk_goal = [.024, .0479, .0718, .0862, .0948]
    #risk_goal = [.08566519, alpha]#, .0862, .0948]
    print("\n\nNow redo -- use all the risk in the last round: ")
    bravo_params = r["bravo"]
    risk_goal = bravo_params["risk_goal"]
    risk_goal[len(risk_goal) - 1] = alpha
    print("New risk goal: " + str(risk_goal))
    find_aurror_params_from_schedule_and_risk(ballots_cast, winner, alpha, model, round_schedule, risk_goal, )
