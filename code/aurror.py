import math
import sys

if (__name__ == '__main__'):

    ballots_cast = 1000
    margin = .1
    alpha = .1
    winner = math.floor((1+margin)*ballots_cast / 2)

    if len(sys.argv) < 5:
        print("python3 aurror.py ballots_cast winner margin [round_schedule]")

    if len(sys.argv) > 1:
        ballots_cast = int(sys.argv[1])

    print(ballots_cast)
