#import athena.tools

class Election():

    def __init__(self):
        pass

    def __init__(self, election):
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



    def print_election(self):
        print("Results of: " + self.name)
        print("Number of valid ballots: " + str(self.print_number(self.ballots_cast)))
        for i, candidate, ballots in zip(range(1,len(self.candidates)+1), self.candidates, self.results):
            print("\t%s %s\t%s" % (i, candidate, self.print_number(ballots)))


    def print_election_info(self):
        print("Number of valid ballots: " + str(self.ballots_cast))
        print("(Declared) Votes for winner: " + str(self.winner))

    def print_number(self, val):
        return "{:,}".format(val).replace(","," ")

