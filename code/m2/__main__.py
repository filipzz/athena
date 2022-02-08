import json

from scipy.stats import binom
from scipy.signal import convolve
from math import log, ceil, floor
from athena.athena import AthenaAudit


def f(p, n, x):
    return binom.pmf(x, n, p)


def g(p, n, x):
    return 1 - binom.cdf(x - 1, n, p)

def minerva2(margin, rounds, observations):
    """"
    Minerva2 RLA

    ----------------
    :parameter margin - margin for the race
    :parameter rounds - audit's vector of round schedule
    :parameter observations - audit's vector of observations (for the declared winner)
    """
    pa = (1 + margin) / 2
    p = .5
    prevO = 0
    prevR = 0
    results = []
    for i in range(min(len(rounds), len(observations))):
        if i == 0:
            bravoP = 1
            bravoPa = 1
        else:
            bravoP = f(p, prevR, prevO)
            bravoPa = f(pa, prevR, prevO)

        bravoCurP = f(p, rounds[i], observations[i])
        bravoCurPa = f(pa, rounds[i], observations[i])

        probP = bravoP * g(p, rounds[i] - prevR, observations[i] - prevO)
        probPa = bravoPa * g(pa, rounds[i] - prevR, observations[i] - prevO)
        pval = probP / probPa

        # print(i+1, pval)
        results.append({
            'round': i + 1,
            'bravoP': bravoCurP,
            'bravoPa': bravoCurPa,
            'probP': probP,
            'probPa': probPa,
            'sigma': bravoCurP / bravoCurPa,
            'LR': bravoCurPa / bravoCurP,
            'pval': pval
        })
        prevO = observations[i]
        prevR = rounds[i]
    return results

if __name__ == '__main__':


    with open("minerva2_data_10.json", 'r') as fileW:
        dataFile = json.load(fileW)

    #print(dataFile)
    #print(len(dataFile["results"]))

    case = 1

    for data in dataFile["results"]:

        #print(data)
        margin = data["margin"]
        risk_limit = data["risk_limit"]
        lr = 1

        print()
        print(case)
        print("margin:", margin, "risk limit:", risk_limit, "rounds:", data['rounds'])
        case = case + 1
        my_round_schedule = []
        my_pstops = []
        my_pvals = []

        for round in range(data["rounds"]):
            #print()
            w = AthenaAudit("minerva", lr * risk_limit, lr * risk_limit)
            # we take into account observations

            if round > 0:
                rds = data['round_sizes'][0:(round)]
            else:
                rds = [0]
            #print(rds)
            predicted_round_size = w.find_next_round_size(margin, [], data["sprobs"][round], 0, 0)
            #print(round,
            #      " requested: ", data["sprobs"][round] ,
            #      " predicted: ", predicted_round_size,
            #      " -> ", max(rds) + predicted_round_size['size']
            #      )
            my_round_schedule.append(max(rds) + predicted_round_size['size'])
            my_pstops.append(predicted_round_size['prob_stop'])

            rounds = data['round_sizes'][0:(round + 1)]
            observations = data['samples']['Alice'][0:(round + 1)]
            #print(round, " ", rounds, " ", observations)

            # evaluate
            results = minerva2(margin, rounds, observations)
            my_pvals.append(results[-1]['pval'])
            #print(results)
            lr = results[-1]['LR']
            #print("next round adjustement: " + str(lr))

        dif_pvals = []
        dif_pstops = []
        dif_rounds = []
        for round in range(len(data['round_sizes'])):
            dif_pvals.append(my_pvals[round] - data["risk"][round])
            dif_pstops.append(my_pstops[round] - data["sprobs"][round])
            dif_rounds.append(my_round_schedule[round] - data['round_sizes'][round])

        print("Data:", data['round_sizes'], data['samples']['Alice'])
        #print(dif_rounds)
        #print(dif_pstops)
        #print(dif_pvals)
        print("round schedule:", my_round_schedule)
        print("pstops:", my_pstops)
        print("pvals: ", my_pvals)

        del(w)
        # predict next round size
