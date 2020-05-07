#import athena.tools
import heapq
import json
import sys

class Election():

    def __init__(self):
        self.ballots_cast = []
        self.candidates = []
        self.results = []
        self.winners = []
        self.name = []
        self.model = ""
        self.declared_winners = []
        self.declared_losers = []
        pass

    def __init__(self, election = None):
        #if election is None:
        self.ballots_cast = []
        self.candidates = []
        self.results = []
        self.winners = []
        self.name = []
        self.model = ""
        self.declared_winners = []
        self.declared_losers = []
        #else:
        if "ballots_cast" in election:
            self.ballots_cast = election["ballots_cast"]

        if "candidates" in election:
            self.candidates = election["candidates"]

        if "results" in election:
            self.results = election["results"]

        if "winners" in election:
            self.winners = election["winners"]

        if "name" in election:
            self.name = election["name"]

        if "model" in election:
            self.model = election["model"]

        # we store information about declared winners and declared losers
        self.declared_winners = []
        self.declared_losers = []

        self.find_winners()

    def read_from_file(self, file_name, contest):
        with open(file_name, 'r') as f:
            data = json.load(f)

        self.ballots_cast = data["total_ballots"]

        info = data[contest]
        self.candidates = info["candidates"]
        self.results = info["votes"]
        self.winners = 1
        self.declared_winners = []
        self.declared_losers = []
        self.name = contest

        self.find_winners()


    def find_winners(self):
        if len(self.results) > 0:
            self.winners_min = min(heapq.nlargest(self.winners, self.results)) # this is the min number of votes to get to be a winner
            for candidate_id, candidate_name, candidate_result in zip(range(len(self.results)), self.candidates, self.results):
                if candidate_result >= self.winners_min:
                    self.declared_winners.append(candidate_id)
                else:
                    self.declared_losers.append(candidate_id)

            if len(self.declared_winners) > self.winners:
                raise ValueError("Too many winners")



    def print_election(self):
        print("Results of: " + self.name)
        print("Number of valid ballots: " + str(self.print_number(self.ballots_cast)))
        for i, candidate, ballots in zip(range(1,len(self.candidates)+1), self.candidates, self.results):
            if ballots >= self.winners_min:
                print("\t%s* %s\t%s" % (i, candidate, self.print_number(ballots)))
            else:
                print("\t%s %s\t%s" % (i, candidate, self.print_number(ballots)))


    def print_election_info(self):
        print("Number of valid ballots: " + str(self.ballots_cast))
        print("(Declared) Votes for winner: " + str(self.winner))

    def print_number(self, val):
        #return "{:,}".format(val).replace(","," ")
        return val

    def get_candidates(self):
        return self.candidates


