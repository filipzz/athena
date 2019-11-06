# Aurror - AUdit: Risk-limiting and ROund-by-Round



# Usage

Typical use:

```bash
python3 code/aurror.py --new raceName --alpha .1 --total 10000  --candidates "Candidate A" CandidateB CandidateC --ballots 5000 3000 2000 --round_schedule 200
```

A new folder: **elections/** will be created in the current path.

Then parameter **--new raceName** will create a folder **elections/raceName** that stores election data.

## Help

```
python3 code/aurror.py -h
```

returns:

```
usage: aurror.py [-h] [-v] [-n NEW] [-a ALPHA] [-t TOTAL]
                 [-c [CANDIDATES [CANDIDATES ...]]]
                 [-b [BALLOTS [BALLOTS ...]]] [-r ROUNDS [ROUNDS ...]]
                 [-w WINNERS] [-e ELECTION]

This program lets for computing AURROR parameters.

optional arguments:
  -h, --help            show this help message and exit
  -v, -V, --version     shows program version
  -n NEW, --new NEW     creates new election folder where all data are stored
  -a ALPHA, --alpha ALPHA
                        set alpha (risk limit) for the election
  -t TOTAL, --total TOTAL
                        set number of valid ballots cast
  -c [CANDIDATES [CANDIDATES ...]], --candidates [CANDIDATES [CANDIDATES ...]]
                        set the candidate list (names)
  -b [BALLOTS [BALLOTS ...]], --ballots [BALLOTS [BALLOTS ...]]
                        set the list of ballots cast for every candidate
  -r ROUNDS [ROUNDS ...], -rs ROUNDS [ROUNDS ...], --rounds ROUNDS [ROUNDS ...], --round_schedule ROUNDS [ROUNDS ...]
                        set the round schedule
  -w WINNERS, --winners WINNERS
                        set number of winners for the given race
  -e ELECTION, --election ELECTION
                        set the election to read
```

## Sample output

```
Results of: raceName
Number of valid ballots: 10000
	1 Candidate A	5000
	2 CandidateB	3000
	3 CandidateC	2000

AURROR parameters: 
Alpha:  0.1
Model:  bin
Round schedule: [200]


Candidate A (5000) vs CandidateB (3000)
	Effective round schedule: [160]
	BRAVO risk: [0.08189835]
	BRAVO pstop: [0.9031591]
	BRAVO kmins: [95]
		AVG:	919.2326324555735
		AVG*:	144.5054564804985

	AURROR kmins:		[90]
	AURROR risk: [0.06641127]
	AURROR pstop: [0.95576613]
		AVG:	506.79353804690834
		AVG*:	152.92258085618553


Candidate A (5000) vs CandidateC (2000)
	Effective round schedule: [140]
	BRAVO risk: [0.08264516]
	BRAVO pstop: [0.99592736]
	BRAVO kmins: [89]
		AVG:	167.93827765816798
		AVG*:	139.42983106820066

	AURROR kmins:		[79]
	AURROR risk: [0.07526385]
	AURROR pstop: [0.99994586]
		AVG:	140.37141661522148
		AVG*:	139.9924200690771


CandidateB (3000) vs CandidateC (2000)
	Effective round schedule: [100]
	BRAVO risk: [0.05283925]
	BRAVO pstop: [0.57330717]
	BRAVO kmins: [61]
		AVG:	2190.794843888754
		AVG*:	57.330717471658076

	AURROR kmins:		[59]
	AURROR risk: [0.04431304]
	AURROR pstop: [0.62253268]
		AVG:	1949.589887001293
		AVG*:	62.25326761221851
```
