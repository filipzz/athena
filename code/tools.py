import numpy as np
import codecs, json

def find_ratio(a, b):
    ratio = []
    for aa, bb in zip(a, b):
        if bb == 0:
            ratio.append(0.0)
        else:
            ratio.append(aa/bb)
    return ratio


def read_table(file_to_read):
    with open(file_to_read, 'r') as f:
        data = json.load(f)
    return np.array(data)

def save_table(table_to_save, file_to_save):
    with open(file_to_save, 'w') as f:
        json_dump = json.dumps(table_to_save, cls=NumpyEncoder)
        #print(json_dump)
        f.write(json_dump)
        #json.dump(json_dump, f)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def print_election(election_info):
    print("Results of: " + election_info["name"])
    print("Number of valid ballots: " + str(print_number(election_info["ballots_cast"])))
    for i, candidate, ballots in zip(range(1,len(election_info["candidates"])+1), election_info["candidates"], election_info["results"]):
        print("\t%s %s\t%s" % (i, candidate, print_number(ballots)))
    #print("(Declared) Votes for winner: " + str(winner))
    #print("Margin: " + str(margin))
    print("\nParameters: ")
    print("Alpha:  " + str(election_info["alpha"]))
    print("Delta:  " + str(election_info["delta"]))
    print("Model:  " + str(election_info["model"]))


def print_election_info(ballots_cast, winner, margin, alpha, model):
    print("Number of valid ballots: " + str(ballots_cast))
    print("(Declared) Votes for winner: " + str(winner))
    print("Margin: " + str(margin))
    print("Alpha:  " + str(alpha))
    print("Model:  " + str(model))

def print_number(val):
    return "{:,}".format(val).replace(","," ")
