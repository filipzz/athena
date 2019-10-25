from fractions import Fraction
from sympy import S, N
from sympy.stats import Binomial, Hypergeometric, density

import numpy as np
import rla as rla


def __init__(self):
    pass


def calculate_bad_luck_cum_probab_table_b2_sympy(roundSize, winner, ballotsCast, alpha, what, model):
    sum = S("0")
    ballotsHalf = np.floor(np.longdouble(ballotsCast)/2)
    wnR = np.floor(np.longdouble(ballotsCast)/2)
    pNotFinishedYet = 1
    if what == "risk":
        p = S("0.5")
        q = (1 - p)
    else:
        p = S(winner)/S(ballotsCast)
        q = 1 - p


    if model == "bin":
        max = rla.bravo_kmin(ballotsCast, winner, alpha, roundSize)
    else:
        max = rla.bravo_like_kmin(ballotsCast, winner, alpha, roundSize)

    if max <= roundSize:

        pTable = [S("0")] * (roundSize)
        pTabletmp = [S("0")] * (roundSize)

        #print(pTabletmp)

        pTableC = [[S("0")] * (roundSize)  for i in range(max)]#] * roundSize
        pTableC[0][0] = (1-p)
        pTableC[1][0] = (p)

        pTableCx = [[S("0")] * (roundSize) for i in range(max)]
        pTableCx[0][0] = 1
        pTableCx[1][0] = 1


        #print(">>> " + str(roundSize) + "\t" + str(max))
        #print("--" + str(len(pTable)) + "\t" + str(len(pTableC)))

        for i in range(1, roundSize):
            if model == "bin":
                kmin = rla.bravo_kmin(ballotsCast, winner, alpha, i+1)
            else:
                kmin = rla.bravo_like_kmin(ballotsCast, winner, alpha, i+1)

            pTableC[0][i] = pTableC[0][i-1] * (1-p)
            pTableCx[0][i] = pTableCx[0][i-1]
            for k in range(kmin):
                #print(str(i) + "\t" + str(k))
                pTableC[k][i] = pTableC[k][i-1] * (1-p) + pTableC[k-1][i-1] * p
                pTableCx[k][i] = pTableCx[k][i-1] + pTableCx[k-1][i-1]


#        for k in range(0, kmin):
#            strg = ""
#            for i in range(0, roundSize):
#                strg += "\t{:,.10f}".format(pTableC[k][i])
#            print(strg + "\n")

        #for k in range(0, kmin):
        #strg = ""
        #for i in range(0, roundSize):
        #strg += "\t{:,.10f}".format(float(pTableC[9][8]))
        #print(strg + "\n")

        for i in range(roundSize):
            sum = 0
            for k in range(max):
                sum = sum + pTableC[k][i]

            pTabletmp[i] = sum

        sum = np.longdouble(0)
        for i in range(1,roundSize):
            pTable[i] = pTabletmp[i-1] - pTabletmp[i]
            sum = sum + pTable[i]

    print("sympy: " + str(N(sum, 50)))

    return  {"pTableC": pTableC, "pTableCx" : pTableCx, "pTable" : pTable, "sum" : sum}


# finds kmin for a given round that is smaller than the goal
def next_round_risk(ballotsCast, winner, alpha, n, goal, dist, prevRoundSize, prvRoundKmin):
    sum = S("0")
    ballotsHalf = S(ballotsCast) / 2

    # we first compute the risk that is used by the kmin computed in "regular" way -- according to Bravo stoppin rule
    if dist == "bin":
        kmin = rla.bravo_kmin(ballotsCast, winner, alpha, n)
        X = Binomial('X', n, S.Half)
    else:
        kmin = rla.bravo_like_kmin(ballotsCast, winner, alpha, n)
        X = Hypergeometric('X', ballotsCast, ballotsHalf, n)

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


#
#
# next functions are for comparison only: they use different number formats floats/numpy/fraction
#
#

def calculate_bad_luck_cum_probab_table_b2(roundSize, winner, ballotsCast, alpha, what, model):
    sum = 0
    ballotsHalf = np.floor(ballotsCast/2)
    wnR = np.floor(ballotsCast/2)
    pNotFinishedYet = 1
    if what == "risk":
        p = 1/2
        q = 1 - p
    else:
        p = winner/ballotsCast
        q = 1 - p


    if model == "bin":
        max = rla.bravo_kmin(ballotsCast, winner, alpha, roundSize)
    else:
        max = rla.bravo_like_kmin(ballotsCast, winner, alpha, roundSize)

    if max <= roundSize:

        pTable = [0] * (roundSize)
        pTabletmp = [0] * (roundSize)

        #print(pTabletmp)

        pTableC = [[0] * (roundSize)  for i in range(max)]#] * roundSize
        pTableC[0][0] = 1-p
        pTableC[1][0] = p


        #print(">>> " + str(roundSize) + "\t" + str(max))
        #print("--" + str(len(pTable)) + "\t" + str(len(pTableC)))

        for i in range(1, roundSize):
            if model == "bin":
                kmin = rla.bravo_kmin(ballotsCast, winner, alpha, i+1)
            else:
                kmin = rla.bravo_like_kmin(ballotsCast, winner, alpha, i+1)

            pTableC[0][i] = pTableC[0][i-1] * (1-p)
            for k in range(kmin):
                #print(str(i) + "\t" + str(k))
                pTableC[k][i] = pTableC[k][i-1] * (1-p) + pTableC[k-1][i-1] * p


        #for k in range(0, kmin):
        #strg = ""
        #for i in range(0, roundSize):
        #strg += "\t{:,.10f}".format(float(pTableC[9][8]))
        #print(strg + "\n")


        for i in range(roundSize):
            sum = 0
            for k in range(max):
                sum = sum + pTableC[k][i]

            pTabletmp[i] = sum

        sum = 0
        for i in range(1,roundSize):
            pTable[i] = pTabletmp[i-1] - pTabletmp[i]
            sum += pTable[i]

    print("float: " + str(sum))

    return  { "pTable" : pTable, "sum" : sum}

def calculate_bad_luck_cum_probab_table_b2_longdouble(roundSize, winner, ballotsCast, alpha, what, model):
    sum = 0
    ballotsHalf = np.floor(np.longdouble(ballotsCast)/2)
    wnR = np.floor(np.longdouble(ballotsCast)/2)
    pNotFinishedYet = 1
    if what == "risk":
        p = np.longdouble(1/2)
        q = np.longdouble(1 - p)
    else:
        p = np.longdouble(winner/ballotsCast)
        q = 1 - p


    if model == "bin":
        max = rla.bravo_kmin(ballotsCast, winner, alpha, roundSize)
    else:
        max = rla.bravo_like_kmin(ballotsCast, winner, alpha, roundSize)

    if max <= roundSize:

        pTable = [np.longdouble(0)] * (roundSize)
        pTabletmp = [np.longdouble(0)] * (roundSize)


        pTableC = [[np.longdouble(0)] * (roundSize)  for i in range(max)]#] * roundSize
        pTableC[0][0] = np.longdouble(1-p)
        pTableC[1][0] = np.longdouble(p)


        for i in range(1, roundSize):
            if model == "bin":
                kmin = rla.bravo_kmin(ballotsCast, winner, alpha, i+1)
            else:
                kmin = rla.bravo_like_kmin(ballotsCast, winner, alpha, i+1)

            pTableC[0][i] = pTableC[0][i-1] * (1-p)
            for k in range(kmin):
                #print(str(i) + "\t" + str(k))
                pTableC[k][i] = pTableC[k][i-1] * (1-p) + pTableC[k-1][i-1] * p



        for i in range(roundSize):
            sum = 0
            for k in range(max):
                sum = sum + pTableC[k][i]

            pTabletmp[i] = sum

        sum = np.longdouble(0)
        for i in range(1,roundSize):
            pTable[i] = pTabletmp[i-1] - pTabletmp[i]
            sum = sum + pTable[i]

    print("numpy: " + str(sum))

    return  { "pTable" : pTable, "sum" : sum}




def calculate_bad_luck_cum_probab_table_b2_frac(roundSize, winner, ballotsCast, alpha, what, model):
    sum = 0
    ballotsHalf = Fraction(ballotsCast,2)
    wnR = Fraction(ballotsCast,2)
    pNotFinishedYet = 1
    if what == "risk":
        p = Fraction(1, 2)
        q = 1 - p
    else:
        p = Fraction(winner, ballotsCast)
        q = 1 - p


    if model == "bin":
        max = rla.bravo_kmin(ballotsCast, winner, alpha, roundSize)
    else:
        max = rla.bravo_like_kmin(ballotsCast, winner, alpha, roundSize)

    if max <= roundSize:

        pTable = [0] * (roundSize)
        pTabletmp = [Fraction(0,1)] * (roundSize)

        #print(pTabletmp)

        pTableC = [[Fraction(0,1)] * (roundSize)  for i in range(max)]#] * roundSize
        pTableC[0][0] = 1-p
        pTableC[1][0] = p


        #print(">>> " + str(roundSize) + "\t" + str(max))
        #print("--" + str(len(pTable)) + "\t" + str(len(pTableC)))

        for i in range(1, roundSize):
            if model == "bin":
                kmin = rla.bravo_kmin(ballotsCast, winner, alpha, i+1)
            else:
                kmin = rla.bravo_like_kmin(ballotsCast, winner, alpha, i+1)

            pTableC[0][i] = pTableC[0][i-1] * (1-p)
            for k in range(kmin):
                #print(str(i) + "\t" + str(k))
                pTableC[k][i] = pTableC[k][i-1] * (1-p) + pTableC[k-1][i-1] * p


        #for k in range(0, kmin):
        #strg = ""
        #for i in range(0, roundSize):
        #strg += "\t{:,.10f}".format(float(pTableC[9][8]))
        #print(strg + "\n")


        for i in range(roundSize):
            sum = 0
            for k in range(max):
                sum = sum + pTableC[k][i]

            pTabletmp[i] = sum

        sum = 0
        for i in range(1,roundSize):
            pTable[i] = pTabletmp[i-1] - pTabletmp[i]
            sum = sum + pTable[i]

    print("frac:  " + str(float(sum)))

    return  {"pTable" : pTable, "sum" : sum}
