import heapq
import sys
import json
import requests
from urllib import parse

class Contest():


    def __init__(self, contest = None):
        self.ballots_cast = 0 # to be removed -> contest_ballots
        self.contest_ballots = 0
        self.tally = []
        self.candidates = []
        self.results = []
        self.winners = 1 # to be removed -> num_winners #number of winners
        self.num_winner = 1
        self.num_candidates = 0
        self.name = []
        self.min_to_win = 0
        self.model = ""
        self.reported_winners = []
        self.declared_winners = []
        self.declared_losers = []
        self.data = None
        self.contest_type = ""
        if contest is not None:
            print(contest)
            #if "contest_ballots" in contest:
            #    self.ballots_cast = contest["contest_ballots"]
            #    self.contest_ballots = contest["contest_ballots"]

            if "candidates" in contest: # to be removed
                self.candidates = contest["candidates"]

            if "results" in contest: # to be removed
                self.results = contest["results"]

            if "num_winners" in contest:
                self.winners = contest["num_winners"]
                self.num_winner = contest["num_winners"]

            if "name" in contest:
                self.name = contest["name"]

            if "model" in contest:
                self.model = contest["model"]

            if "tally" in contest:
                for candidate, result in contest["tally"].items():
                    self.candidates.append(candidate) #info["candidates"]
                    self.results.append(result)
                self.tally = contest["tally"]
                self.num_candidates = len(self.candidates)

            if "reported_winners" in contest:
                self.reported_winners = contest["reported_winners"]



            if "contest_type" in contest:
                self.contest_type = contest["contest_type"]

            # we store information about declared winners and declared losers
            self.declared_winners = []
            self.declared_losers = []

            self.find_winners()

    #def __str__(self):
    #    return f"""{{"contest_ballots": {self.ballots_cast}, "num_winners": {self.winners}, "reported_winners": {self.reported_winners}, "contest_type": "{self.contest_type}", "tally": {self.tally}}}"""

    def __repr__(self):
        return f'{{"contest_ballots": {self.ballots_cast}, "num_winners": {self.winners}, "reported_winners": {self.reported_winners}, "contest_type": "{self.contest_type}", "tally": {self.tally!r}, "declared_winners": {self.declared_winners}, "declared_losers": {self.declared_losers}}}'

    def read_election_data(self, file_name):
        try:
            parsed = parse.urlparse(file_name)
            if all([parsed.scheme, parsed.netloc, parsed.path]):
                self.data = json.loads(requests.get(file_name).text)
            else:
                with open(file_name, 'r') as f:
                    self.data = json.load(f)
        except:
            raise Exception("Can't read the file")
        self.ballots_cast = self.data["total_ballots"]


    def load_contest_data(self, contest, data = None):

        if data is not None:
            self.data = data
        info = self.data["contests"][contest]

        print("results", self.results)
        self.results = []
        self.candidates = []
        for candidate, result in info["tally"].items():
            self.candidates.append(candidate) #info["candidates"]
            self.results.append(result)

        self.winners = info["num_winners"]
        self.reported_winners = info["reported_winners"]
        self.declared_winners = []
        self.declared_losers = []
        self.name = contest

        self.find_winners()



    def find_winners(self):
        if len(self.results) > 0:
            self.min_to_win = min(heapq.nlargest(self.winners, self.results)) # this is the min number of votes to get to be a winner
            for candidate_id, candidate_result in zip(range(len(self.results)), self.results):
                if candidate_result >= self.min_to_win:
                    self.declared_winners.append(candidate_id)
                else:
                    self.declared_losers.append(candidate_id)

            reported_list = self.reported_winners
            declared_list = self.declared_winners
            # check if the list of reported winners matches winners from the vote-count
            for reported, computed in zip(reported_list, declared_list):
                if reported != self.candidates[computed]:
                    raise ValueError("Incorrect reported winners")

            if len(self.declared_winners) > self.winners:
                raise ValueError("Too many winners")



    def print_election(self):
        #print("Results of: " + self.name)
        #print("Number of contest ballots: " + str(self.print_number(self.ballots_cast)))
        for i, candidate, ballots in zip(range(1,len(self.candidates)+1), self.candidates, self.results):
            if ballots >= self.min_to_win:
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


