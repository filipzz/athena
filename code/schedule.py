import rla as rla
import risk as risk
from sympy import S

def __init__():
    pass


def main():
    print(rla.bravo_kmin(100, 60, .1, 13))

    # Setting up the parameters for the audit
    roundSize = 22
    winner = 600
    ballotsCast = 1000
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


    # initializing variables
    pTableRbR = [S("0")] * (maxNumberOfRounds)
    max = rla.bravo_kmin(ballotsCast, winner, alpha, upperLimit)
    pTableCRbR = [[S("0")] * (maxNumberOfRounds)  for i in range(max)]
    roundStartAt = 0
    kminNew = [0] * maxNumberOfRounds

    nrr = risk.next_round_risk(ballotsCast, winner, alpha, roundSchedule[0], riskGoal[0], "bin", 0, 0)
    kminNew[0] = nrr["kmin"]

    print(str((nrr["sum"])))

    print(str(nrr["kmin"]))

    # finding round numbers:
    # - kmin
    # - probability of stopping






if __name__ == '__main__':
    main()
