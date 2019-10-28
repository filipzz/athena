import rla as rla
import risk as risk
from sympy import S, N
from sympy.stats import Binomial, Hypergeometric, density
import math


def __init__():
    pass


def main():
    print(rla.bravo_kmin(100, 60, .1, 13))

    # Setting up the parameters for the audit
    roundSize = 22
    margin = .2
    ballotsCast = 1000
    winner = math.floor((1+margin)/2* ballotsCast)
    roundSchedule = [19, 50, 120]
    maxNumberOfRounds = len(roundSchedule)
    alpha = .1
    what = "risk"
    model = "bin"



    # Finiding BRAVO ballot by ballot risk and stopping probabilities
    upperLimit = roundSchedule[maxNumberOfRounds - 1]
    riskEval = risk.calculate_bad_luck_cum_probab_table_b2_sympy(upperLimit, winner, ballotsCast, alpha, "risk", model)
    probEval = risk.calculate_bad_luck_cum_probab_table_b2_sympy(upperLimit, winner, ballotsCast, alpha, "prob", model)
    print(riskEval["sum"])

    riskTable = riskEval["pTable"]
    riskGoal = [S("0")] * (maxNumberOfRounds)
    probTable = probEval["pTable"]
    probStop = [S("0")] * (maxNumberOfRounds)


    # in riskGoal[] we will store how much risk can be spent for each round
    for round in range(maxNumberOfRounds):
        upperLimitRound = roundSchedule[round]
        riskGoal[round] = sum(riskTable[0:upperLimitRound])
        probStop[round] = sum(probTable[0:upperLimitRound])
        print(str(round+1) + "\t" + str(roundSchedule[round]) + "\t" + str(riskGoal[round]) + "\t" + str(upperLimit))


    print("Risk goal: " + str(riskGoal))
    # initializing variables
    pTableRbR = [S("0")] * (maxNumberOfRounds)
    max = rla.bravo_kmin(ballotsCast, winner, alpha, upperLimit)
    pTableCRbR = [[S("0")] * (maxNumberOfRounds)  for i in range(max)]
    roundStartAt = 0
    ballotsHalf = S(ballotsCast) / 2



    # finding round numbers:
    # - kmin
    # - probability of stopping

    # first round is "special"
    # {rskConsumed, kminPrime} =
    #   FirstRoundRisk[ball, winner, alpha, roundSchedule[[1]],
    #    riskGoal[[1]] - usedRisk, mode];
    # Print[rskConsumed, "\t", kminPrime];
    # kminNew[[1]] = kminPrime;

    nrr = risk.next_round_risk(ballotsCast, winner, alpha, roundSchedule[0], riskGoal[0], "bin", 0, 0)

    kminPrime = nrr["kmin"]
    kminNew = [kminPrime] * maxNumberOfRounds

    print(str((nrr["sum"])))

    print(str(nrr["kmin"]))

    # For[i = 0, i < kminPrime, i++,
    #   If[mode == "bin",
    #     	pTableCRbR[[i + 1, 1]] =
    #       PDF[BinomialDistribution[roundSchedule[[1]] - roundStartAt,
    #         wn/ball], i];,
    #     	pTableCRbR[[i + 1, 1]] =
    #       PDF[HypergeometricDistribution[
    #         roundSchedule[[1]] - roundStartAt, wn, ball], i];
    #     ];
    #   ];

    # we do it for the first round first
    # TODO: we need to add hypergeometric (after we figure out how to deal with invalid votes)
    for i in range(kminPrime):
        X = Binomial('X', roundSchedule[0], S.Half)
        pTableCRbR[i][0] = density(X).dict[i]
        #print(str(i) + "\t" + str(N(density(X).dict[i])))

    riskSpentSoFar = S("0")
    for i in range(kminPrime):
        riskSpentSoFar = riskSpentSoFar + pTableCRbR[i][0]

    print("risk after first round: ", str(N(1- riskSpentSoFar)))


    # (* Now the main loop going for the following rounds *)
    # For[i = 2,
    #  i <= Length[roundSchedule], i++,
    #  Print["\n\n\t\t\tSTARTING NEW ROUND ", i];
    #  (*Print[pTableCRbR[[;;,i-1]]//N];*)
    #
    #  Print[1 - Total[pTableCRbR[[;; , i - 1]]] // N];
    #  roundStartAt = roundSchedule[[i - 1]];
    #
    #  (* now the part that we are sure its is gonna work - starting from k \
    # = kMin[-1] + 1 *)
    #  For[j = 0, j < kminNew[[i - 1]], j++,
    #   For[k = 0, k < kminNew[[i - 1]], k++,
    #     pTableCRbR[[k + 1, i]] +=
    #      pTableCRbR[[j + 1, i - 1]] PDF[
    #        BinomialDistribution[roundSchedule[[i]] - roundStartAt,
    #         wn/ball], k - j];
    #     (*If[i+j+k\[Equal]100,Print[i, "\t", j,"\t",k,"\t",
    #     pTableCRbR[[j+1,i-1]]//N,"\t", PDF[BinomialDistribution[
    #     roundSchedule[[i]]-roundStartAt,wn/ball],k-j]//N,"\t",
    #     pTableCRbR[[k+1,i]]//N]];*)
    #     ];
    #   ];
    #
    #  Print[i, "\t", kminNew[[i - 1]]];
    #
    #  (* we compute what is the current risk spent *)
    #
    #  riskSpentSoFar = Total[pTableCRbR[[;; , i]]];
    #
    #
    #  correctRiskLevel = 1;
    #
    #  (* now we need to find what is kminPrime for the current round - we \
    # will try to add new, larger values of k,
    #  as long as the riskGoal is not exceeded *)
    #  k = kminNew[[i - 1]];
    #  While[ correctRiskLevel == 1 ,
    #   For[j = 0,
    #    j < Min[kminNew[[i - 1]], roundSchedule[[i]] - roundStartAt], j++,
    #    pTableCRbR[[k + 1, i]] +=
    #     pTableCRbR[[j + 1, i - 1]] PDF[
    #       BinomialDistribution[roundSchedule[[i]] - roundStartAt,
    #        wn/ball], k - j];
    #    (*Print[i, "\t", j,"\t",k,"\t",pTableCRbR[[j+1,i-1]]//N,"\t", PDF[
    #    BinomialDistribution[roundSchedule[[i]]-roundStartAt,wn/ball],k-j]//
    #    N,"\t",pTableCRbR[[k+1,i]]//N];*)
    #    ];
    #
    #   riskSpentSoFar = Total[pTableCRbR[[;; , i]]];
    #   (*Print[k,"\t>> ", 1-riskSpentSoFar//N];*)
    #
    #   If[1 - riskSpentSoFar < riskGoal[[i]],
    #    kminNew[[i]] = k + 1;
    #    correctRiskLevel = 0;
    #    ];
    #   k++;
    #   ]
    #  ]

    print(str(kminNew))


    # Now the main loop going for the following rounds
    for i in range(1, maxNumberOfRounds):
        print("STARTING NEW ROUND " + str(i+1))

        riskSpentSoFar = S("0")
        for xi in range(kminPrime):
            riskSpentSoFar = riskSpentSoFar + pTableCRbR[xi][i-1]

        print("risk spent up to: ", str(i), " round: ", str(N(1- riskSpentSoFar)))
        roundStartAt = roundSchedule[i-1]

        # now the part that we are sure its is gonna work - starting from k =
        #  kMin[-1] + 1
        for j in range(kminNew[i-1]):
            for k in range(j,kminNew[i-1]):
                X = Binomial('X', roundSchedule[i] - roundStartAt, S.Half)
                pTableCRbR[k][i] = pTableCRbR[k][i] + pTableCRbR[j][i-1] * density(X).dict[k-j]
                #print(str(roundSchedule[i] - roundStartAt), "\t", str(j), "\t", str(k), "\t",  str(N(pTableCRbR[j][i-1])), "\t", str(N(density(X).dict[k-j])) )
                #print("pTableCRbR[", str(k), ", ", str(i), "] = ", str(N(pTableCRbR[k][i])))

        print(str(i) + "\t" + str(kminNew[i-1]))

        print(kminPrime)


        # we compute what is the current risk spent
        riskSpentSoFar = S("0")
        for xi in range(kminNew[i-1]):
            riskSpentSoFar = riskSpentSoFar + pTableCRbR[xi][i]

        print("risk spent so far: (before last while)", str(N(riskSpentSoFar)))

        correctRiskLevel = 1

        # now we need to find what is kminPrime for the current round -
        #  we will try to add new, larger values of k,
        # as long as the riskGoal is not exceeded

        k = kminNew[i-1]

        print(">>" + str(kminNew[i-1]) + "\t" + str(roundSchedule[i] - roundStartAt))
        while correctRiskLevel == 1 and k <= roundSchedule[i] - roundStartAt + 1:
            for j in range(min(kminNew[i-1], roundSchedule[i] - roundStartAt)):
                X = Binomial('X', roundSchedule[i] - roundStartAt, S.Half)
                if k - j <= roundSchedule[i] - roundStartAt:
                    pTableCRbR[k][i] = pTableCRbR[k][i] + pTableCRbR[j][i-1] * density(X).dict[k-j]
                    #print(str(roundSchedule[i] - roundStartAt), "\t", str(j), "\t", str(k), "\t",  str(N(pTableCRbR[j][i-1])), "\t", str(N(density(X).dict[k-j])) )
                #print("pTableCRbR[", str(k), ", ", str(i), "] = ", str(N(pTableCRbR[k][i])))


            riskSpentSoFar = S("0")
            for xi in range(k+1):
                riskSpentSoFar = riskSpentSoFar + pTableCRbR[xi][i]


            if (1 - N(riskSpentSoFar)) < N(riskGoal[i]):
                kminNew[i] = k + 1
                correctRiskLevel = 0
                print("new kminNew: " + str(kminNew[i]))

            k = k + 1


        print(str(kminNew))










if __name__ == '__main__':
    main()
