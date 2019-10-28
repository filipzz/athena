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

def main():

    # Setting up the parameters for the audit
    roundSize = 22
    margin = .08
    ballots_cast = 1000
    winner = math.floor((1+margin)/2* ballots_cast)
    round_schedule = [301, 518, 916, 1520, 3366]
    alpha = .1
    what = "risk"
    model = "bin"
    max_number_of_rounds = len(round_schedule)


    print("Proposed round sizes: " + str(round_schedule))
    bravo_kmins = map(lambda n: rla.bravo_kmin(ballots_cast, winner, alpha, n), round_schedule )
    print("Corresponding BRAVO kmins: " + str(print_iterator(bravo_kmins)))

    # Finiding BRAVO ballot by ballot risk and stopping probabilities
    upper_limit = round_schedule[max_number_of_rounds - 1]
    risk_eval = risk.calculate_bad_luck_cum_probab_table_b2_sympy(upper_limit, winner, ballots_cast, alpha, "risk", model)
    prob_eval = risk.calculate_bad_luck_cum_probab_table_b2_sympy(upper_limit, winner, ballots_cast, alpha, "prob", model)
    #print(risk_eval["sum"])

    risk_table = risk_eval["p_table"]
    risk_goal = [S("0")] * (max_number_of_rounds)
    prob_table = prob_eval["p_table"]
    prob_stop = [S("0")] * (max_number_of_rounds)


    # in risk_goal[] we will store how much risk can be spent for each round
    for round in range(max_number_of_rounds):
        upper_limit_round = round_schedule[round]
        risk_goal[round] = sum(risk_table[0:upper_limit_round])
        prob_stop[round] = sum(prob_table[0:upper_limit_round])
        #print(str(round+1) + "\t" + str(round_schedule[round]) + "\t" + str(risk_goal[round]) + "\t" + str(upper_limit))


    #print("Risk goal: " + str(risk_goal))
    # initializing variables
    pTableRbR = [S("0")] * (max_number_of_rounds)
    max = rla.bravo_kmin(ballots_cast, winner, alpha, upper_limit)
    p_table_c_rbr = [[S("0")] * (max_number_of_rounds)  for i in range(max)]
    round_start_at = 0
    ballotsHalf = S(ballots_cast) / 2



    # finding round numbers:
    # - kmin
    # - probability of stopping

    # first round is "special"
    # {rskConsumed, kmin_prime} =
    #   FirstRoundRisk[ball, winner, alpha, round_schedule[[1]],
    #    risk_goal[[1]] - usedRisk, mode];
    # Print[rskConsumed, "\t", kmin_prime];
    # kmin_new[[1]] = kmin_prime;

    nrr = risk.next_round_risk(ballots_cast, winner, alpha, round_schedule[0], risk_goal[0], "bin", 0, 0)

    kmin_prime = nrr["kmin"]
    kmin_new = [kmin_prime] * max_number_of_rounds

    #print(str((nrr["sum"])))

    #print(str(nrr["kmin"]))

    # For[i = 0, i < kmin_prime, i++,
    #   If[mode == "bin",
    #     	p_table_c_rbr[[i + 1, 1]] =
    #       PDF[BinomialDistribution[round_schedule[[1]] - round_start_at,
    #         wn/ball], i];,
    #     	p_table_c_rbr[[i + 1, 1]] =
    #       PDF[HypergeometricDistribution[
    #         round_schedule[[1]] - round_start_at, wn, ball], i];
    #     ];
    #   ];

    # we do it for the first round first
    # TODO: we need to add hypergeometric (after we figure out how to deal with invalid votes)
    for i in range(kmin_prime):
        X = Binomial('X', round_schedule[0], S.Half)
        p_table_c_rbr[i][0] = density(X).dict[i]
        #print(str(i) + "\t" + str(N(density(X).dict[i])))

    risk_spent_so_far = S("0")
    for i in range(kmin_prime):
        risk_spent_so_far = risk_spent_so_far + p_table_c_rbr[i][0]

    print("risk after first round: ", str(N(1- risk_spent_so_far)))


    # (* Now the main loop going for the following rounds *)
    # For[i = 2,
    #  i <= Length[round_schedule], i++,
    #  Print["\n\n\t\t\tSTARTING NEW ROUND ", i];
    #  (*Print[p_table_c_rbr[[;;,i-1]]//N];*)
    #
    #  Print[1 - Total[p_table_c_rbr[[;; , i - 1]]] // N];
    #  round_start_at = round_schedule[[i - 1]];
    #
    #  (* now the part that we are sure its is gonna work - starting from k \
    # = kMin[-1] + 1 *)
    #  For[j = 0, j < kmin_new[[i - 1]], j++,
    #   For[k = 0, k < kmin_new[[i - 1]], k++,
    #     p_table_c_rbr[[k + 1, i]] +=
    #      p_table_c_rbr[[j + 1, i - 1]] PDF[
    #        BinomialDistribution[round_schedule[[i]] - round_start_at,
    #         wn/ball], k - j];
    #     (*If[i+j+k\[Equal]100,Print[i, "\t", j,"\t",k,"\t",
    #     p_table_c_rbr[[j+1,i-1]]//N,"\t", PDF[BinomialDistribution[
    #     round_schedule[[i]]-round_start_at,wn/ball],k-j]//N,"\t",
    #     p_table_c_rbr[[k+1,i]]//N]];*)
    #     ];
    #   ];
    #
    #  Print[i, "\t", kmin_new[[i - 1]]];
    #
    #  (* we compute what is the current risk spent *)
    #
    #  risk_spent_so_far = Total[p_table_c_rbr[[;; , i]]];
    #
    #
    #  correct_risk_level = 1;
    #
    #  (* now we need to find what is kmin_prime for the current round - we \
    # will try to add new, larger values of k,
    #  as long as the risk_goal is not exceeded *)
    #  k = kmin_new[[i - 1]];
    #  While[ correct_risk_level == 1 ,
    #   For[j = 0,
    #    j < Min[kmin_new[[i - 1]], round_schedule[[i]] - round_start_at], j++,
    #    p_table_c_rbr[[k + 1, i]] +=
    #     p_table_c_rbr[[j + 1, i - 1]] PDF[
    #       BinomialDistribution[round_schedule[[i]] - round_start_at,
    #        wn/ball], k - j];
    #    (*Print[i, "\t", j,"\t",k,"\t",p_table_c_rbr[[j+1,i-1]]//N,"\t", PDF[
    #    BinomialDistribution[round_schedule[[i]]-round_start_at,wn/ball],k-j]//
    #    N,"\t",p_table_c_rbr[[k+1,i]]//N];*)
    #    ];
    #
    #   risk_spent_so_far = Total[p_table_c_rbr[[;; , i]]];
    #   (*Print[k,"\t>> ", 1-risk_spent_so_far//N];*)
    #
    #   If[1 - risk_spent_so_far < risk_goal[[i]],
    #    kmin_new[[i]] = k + 1;
    #    correct_risk_level = 0;
    #    ];
    #   k++;
    #   ]
    #  ]



    # Now the main loop going for the following rounds
    for i in range(1, max_number_of_rounds):
        print("STARTING NEW ROUND " + str(i+1))

        risk_spent_so_far = S("0")
        for xi in range(kmin_prime):
            risk_spent_so_far = risk_spent_so_far + p_table_c_rbr[xi][i-1]

        print("risk spent up to: ", str(i), " round: ", str(N(1- risk_spent_so_far)))
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

            print(str(i) + "\t" + str(k) + "\t" + str(N(risk_spent_so_far)))


            if (1 - N(risk_spent_so_far)) < N(risk_goal[i]):
                kmin_new[i] = k + 1
                correct_risk_level = 0
                #print("new kmin_new: " + str(kmin_new[i]))

            k = k + 1



    print("Found new Aurror kmins:\t\t" + str(kmin_new))










if __name__ == '__main__':
    main()
