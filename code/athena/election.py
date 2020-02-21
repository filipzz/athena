#import athena.tools

class Election():


    def __init__(self, election):
        self.ballots_cast = election["ballots_cast"] #= ballots_cast
        self.alpha = election["alpha"] #= alpha
        self.delta = election["delta"] #= delta
        self.candidates = election["candidates"] #= candidates
        self.results = election["results"] #= results
        self.winners = election["winners"] #= winners
        self.name = election["name"] #= name
        self.model = election["model"] #= model
        self.pstop = election["pstop"] #= pstop_goal
        self.round_schedule = election["round_schedule"] #= round_schedule
        #self.save_to = "elections/" + name

    def print_election(self):
        print("Results of: " + self.name)
        print("Number of valid ballots: " + str(self.print_number(self.ballots_cast)))
        for i, candidate, ballots in zip(range(1,len(self.candidates)+1), self.candidates, self.results):
            print("\t%s %s\t%s" % (i, candidate, self.print_number(ballots)))
        #print("(Declared) Votes for winner: " + str(winner))
        #print("Margin: " + str(margin))
        print("\nParameters: ")
        print("Alpha:  " + str(self.alpha))
        print("Delta:  " + str(self.delta))
        print("Model:  " + str(self.model))


    def print_election_info(self):
        print("Number of valid ballots: " + str(self.ballots_cast))
        print("(Declared) Votes for winner: " + str(self.winner))
        print("Margin: " + str(self.margin))
        print("Alpha:  " + str(self.alpha))
        print("Model:  " + str(self.model))

    def print_number(self, val):
        return "{:,}".format(val).replace(","," ")

