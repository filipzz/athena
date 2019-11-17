# Aurror - AUdit: Risk-limiting and ROund-by-Round



# Usage

Typical use:

```bash
python3 code/aurror.py --new raceName --ballots 5000 3000 2000 --round_schedule 100 200
```
where:

- **--ballots** is a list of votes each candidate received
- **--round_schedule** is the round schedule for the audit

and with shorter parameternames:

```bash
python3 code/aurror.py -n raceName -b 5000 3000 2000  -r 100 200
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
python3 code/aurror.py --new raceName --alpha .1 --candidates "Albus D." Bob Cedric --ballots 5000 3000 2000 --round_schedule 100 200
```

```
Results of: raceName

Number of valid ballots: 10000
	1 Albus D.	5000
	2 Beatrix	3000
	3 Cedric	2000

AURROR parameters: 
Alpha:  0.1
Model:  bin
Round schedule: [100, 200]


Albus D. (5000) vs Beatrix (3000)
	Effective round schedule: [80, 160]
	BRAVO risk: [0.06235051 0.08189835]
	BRAVO pstop: [0.6862955 0.9031591]
	BRAVO kmins: [50, 95]
		AVG:	864.3289922821481
		AVG*:	89.6018163070731

	AURROR kmins:		[48, 91]
	AURROR risk: [0.04645594 0.07607745]
	AURROR pstop: [0.72018903 0.94721429]
		AVG:	516.2248341824325
		AVG*:	93.93916383508287


Albus D. (5000) vs Cedric (2000)
	Effective round schedule: [70, 140]
	BRAVO risk: [0.07876542 0.08264516]
	BRAVO pstop: [0.95085346 0.99592736]
	BRAVO kmins: [46, 89]
		AVG:	101.37853526706321
		AVG*:	72.8700886770959

	AURROR kmins:		[42, 81]
	AURROR risk: [0.05980467 0.07910063]
	AURROR pstop: [0.9856999  0.99984057]
		AVG:	72.09470846760281
		AVG*:	70.97868682907473


Beatrix (3000) vs Cedric (2000)
	Effective round schedule: [50, 100]
	BRAVO risk: [0.02323915 0.05283925]
	BRAVO pstop: [0.25028037 0.57330717]
	BRAVO kmins: [34, 61]
		AVG:	2178.280825342702
		AVG*:	44.81669892560588

	AURROR kmins:		[33, 59]
	AURROR risk: [0.01641957 0.05205361]
	AURROR pstop: [0.2368758  0.63577295]
		AVG:	1872.868747440554
		AVG*:	51.73350509300488
```


# Risk evaluation (first approach)

To evaluate the risk of a given observation you need to add **--evaluate_risk** parameter, followed with the number
of votes for the winner counted in each round

```
python3 aurror.py -n asd -b 15038 5274 -r 34 57  --alpha 0.1 --evaluate_risk 22 34
```

The sample output.

For this version of software a modified version of Aurror (denoted by Aurror*) is used (we change the way
we find kmins -- we treat every round to be the first round). This approach may lead to going above Bravo risk.

```
Results of: asd
Number of valid ballots: 20312
	1 A	15038
	2 B	5274

AURROR parameters: 
Alpha:  0.1
Model:  bin
Round schedule: [34, 57]


A (15038) vs B (5274)

	Effective round schedule: [34, 57]

	BRAVO kmins: 	[24, 38]
	BRAVO risk: 	[0.0739184 0.0827711]
	BRAVO pstop: 	[0.8566519  0.96022161]
		AVG:	843.0083804970857
		AVG*:	35.02963781549562

	ARLO kmins:	[24, 38]
	ARLO risk:	[0.01215326 0.0169324 ]
	ARLO pstop:	[0.74902808 0.93046317]

	Aurror kmins:	[22, 36]
	Aurror risk:	[0.06072474 0.07293752]
	Aurror pstop:	[0.92086788 0.98214221]
	--- ratio:	[0.06594295 0.07426371]

	Aurror* kmins:	[22, 35]
	Aurror* risk:	[0.06072474 0.08834209]
	Aurror* pstop:	[0.92086788 0.98996194]
	--- ratio:	[0.06594295 0.08923786]

	AUDIT result:
		observed:	[22, 34]
		required:	[22, 35]

		Test passed

		estimated risk (alpha estimation):	0.084000390625
		computed risk (alpha and kmins): 	0.06594294739276789

```

# Acknowledgements

We thank [NSF (1421373 TWC: TTP Option: Small: Open-Audit Voting Systems---Protocol Models and Properties)](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1421373) for funding the implementation of this project.
