# Aurror - AUdit: Risk-limiting and ROund-by-Round



# Usage

Typical use:

```bash
python3 code/aurror.py --new raceName --ballots 5000 3000 2000 --round_schedule 100 200
```
where:

- **--ballots** is a list of votes each candidate received
- **--round_schedule** is the round schedule for the audit
- **--type** is an optional argument that lets one see result of different audity types Aurrror (default) | Bravo/Wald | Arlo

and with shorter parameternames:

```bash
python3 code/aurror.py -n raceName -b 5000 3000 2000  -r 100 200 --type arlo
```

## Finding stopping probabilities

In this mode, one can (roughly) what are the expected round sizes
for a given results:

- **--ballots** (list of declared number of votes cast for each candidate)
- **--pstop** (list of stopping probabilities for the next round)

```bash
python3 aurror.py -n asd -b 60000 40000 --pstop .7 .8 .9 
```

returns:

```bash
[0.7, 0.8, 0.9]
Results of: asd
Number of valid ballots: 100000
	1 A	60000
	2 B	40000

AURROR parameters: 
Alpha:  0.1
Model:  bin
Round schedule: []
setting round schedule


A (60000) vs B (40000)
	margin:	0.2
pstop goal: [0.7, 0.8, 0.9]
round schedule: []
	0.7	[112]
	0.8	[132]
	0.9	[182]
```

If one want to estimate round sizes for the next round, round_schedule parameter needs to be added

```bash
python3 aurror.py -n asd -b 60000 40000 --pstop .5 .8  --rounds 132
[0.5, 0.8]
Results of: asd
Number of valid ballots: 100000
	1 A	60000
	2 B	40000

Parameters: 
Alpha:  0.1
Model:  bin
Round schedule: [132]
setting round schedule


A (60000) vs B (40000)
	margin:	0.2
pstop goal: [0.5, 0.8]
round schedule: [132]
	0.5	[132, 224]
	0.8	[132, 297]
```

To get obtain detailed information about a selected round schedule (e.g., [132, 297])
one needs to call it without **--pstop** parameter.

```bash
python3 aurror.py -n asd -b 60000 40000 --rounds 132 297
Results of: asd
Number of valid ballots: 100000
	1 A	60000
	2 B	40000

Parameters: 
Alpha:  0.1
Model:  bin
Round schedule: [132, 297]


A (60000) vs B (40000)
	margin:	0.2

	Approx round schedule:	[132, 297]
	AURROR kmins:		[75, 165]
	AURROR pstop (tied): 	[0.06933400321906029, 0.08488117767255854]
	AURROR pstop (audit):	[0.798620073240586, 0.9604763404354484]
	AURROR true risk:	[0.08681725584196939, 0.08837404327323274]
```

At the end we may want to check how, for that round schedule Arlo audit would work

```bash
python3 aurror.py -n asd -b 60000 40000 --rounds 132 297 --type arlo
Results of: asd
Number of valid ballots: 100000
	1 A	60000
	2 B	40000

Parameters: 
Alpha:  0.1
Model:  bin
Round schedule: [132, 297]


A (60000) vs B (40000)
	margin:	0.2

	Approx round schedule:	[132, 297]
	ARLO kmins:		[79, 170]
	ARLO pstop (tied): 	[0.014585813499702633, 0.019495722498663753]
	ARLO pstop (audit):	[0.5517707405988952, 0.8681144359578332]
	ARLO true risk:	[0.026434554111860128, 0.022457549017893208]

```

## Wald's sequential test

Wald's sequential test (BRAVO audit) can be seen as a special case of AURROR.
AURROR with round schedule **[1, 2, 3, ..., max]** is the same as Wald's sequential
test that stops after up to **max** ballots checked.

Calling:

```bash
python3 aurror.py -n asd -b 6000 4000  --rounds 17 --type BRAVO
```

Is equivalent to calling:

```bash
python3 aurror.py -n asd -b 6000 4000  --rounds 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17
```


## Help

```
python3 code/aurror.py -h
```

returns:

```
usage: aurror.py [-h] [-v] [-n NEW] [-a ALPHA]
                 [-c [CANDIDATES [CANDIDATES ...]]]
                 [-b [BALLOTS [BALLOTS ...]]] [-t TOTAL]
                 [-r ROUNDS [ROUNDS ...]] [-p PSTOP [PSTOP ...]] [-w WINNERS]
                 [-l LOAD] [--type TYPE] [-e RISK [RISK ...]]

This program lets for computing AURROR parameters.

optional arguments:
  -h, --help            show this help message and exit
  -v, -V, --version     shows program version
  -n NEW, --new NEW     creates new election folder where all data are stored
  -a ALPHA, --alpha ALPHA
                        set alpha (risk limit) for the election
  -c [CANDIDATES [CANDIDATES ...]], --candidates [CANDIDATES [CANDIDATES ...]]
                        set the candidate list (names)
  -b [BALLOTS [BALLOTS ...]], --ballots [BALLOTS [BALLOTS ...]]
                        set the list of ballots cast for every candidate
  -t TOTAL, --total TOTAL
                        set the total number of ballots in given contest
  -r ROUNDS [ROUNDS ...], --rounds ROUNDS [ROUNDS ...], --round_schedule ROUNDS [ROUNDS ...]
                        set the round schedule
  -p PSTOP [PSTOP ...], --pstop PSTOP [PSTOP ...]
                        set stopping probability goals for each round
                        (corresponding round schedule will be found)
  -w WINNERS, --winners WINNERS
                        set number of winners for the given race
  -l LOAD, --load LOAD  set the election to read
  --type TYPE           set the audit type (BRAVO/AURROR)
  -e RISK [RISK ...], --risk RISK [RISK ...], --evaluate_risk RISK [RISK ...]
                        evaluate risk for given audit results
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
