# Athena - Risk Limiting Audit (Round-by-Round)

This library is an implementation of [The ATHENA Class of Risk-Limiting Ballot Polling Audits](https://arxiv.org/pdf/2008.02315.pdf)


# Installation

```bash
python -m pip install git+https://github.com/filipzz/athena.git
```

# Usage

## As a library
See [athena.ipynb](code/athena.ipynb) for examples of the API.

## From the command line

### Entering data from command line

```bash
python -m athena --name contestName --ballots 5000 3000 2000 --pstop .9 .95 --type athena
```
where:

- **--ballots** is a list of votes each candidate received
- **--name** name of a contest
- **--pstop** is a list of stopping probabilities
- **--type** is an optional argument that lets one see result of different audit types **athena** (default) | **bravo** (wald) | **arlo**

The above call would return:

```bash
[[0.9, 145], [0.95, 222]]
```

which means that if *148* ballots were drawn the audit would stop (on average) with probability 90%,
assuming the reported results were correct.
If *213* ballots were drawn, then the probability of completing the audit would be 95%.

The command also supports shorter parameter names, like this:

```bash
python -m athena -n contestName -b 5000 3000 2000  -p .9
```

Note that the default audit type is Athena.


### Reading data from a file

Election data can be read from a json file of the following form:

```json
 {
	"name": "Local Elections 2020",
	"total_ballots": 10000,
	"contests": {
		"contest_1": {
			"contest_ballots": 10000,
			"tally": {
				"A": 6000,
				"B": 4000
			},
			"num_winners": 1,
			"reported_winners": [
				"A"
			],
			"contest_type": "PLURALITY"
		}
    }
}
```

A file may contain many contests.

Then one needs to provide a path to a file (parameter **--file**)  and provide the name of the contest (with the
example above: **-n contest_1**):

```bash
python -m athena --file  athena/test_data/simple.json --name contest_1 --pstop .7
```


# Usage

Athena helps to:

- estimate the number of ballots to be drawn in order to complete audit with a

## Finding stopping probabilities

In this mode, one can (roughly) what are the expected round sizes
for a given results:

- **--ballots** (list of declared number of votes cast for each candidate)
- **--pstop** (list of stopping probabilities for the next round)

```bash
python -m athena -n asd -b 60000 40000 --pstop .7 .8 .9 
```

returns:

```bash
[[0.7, 111], [0.8, 138], [0.9, 179]]
```

If one want to estimate round sizes for the next round, round_schedule parameter needs to be added

```bash
python -m athena -n asd -b 60000 40000 --pstop .5 .8  --rounds 132
[[0.5, 75], [0.8, 138]]
```

To get obtain detailed information about a selected round schedule (e.g., [132, 297])
one needs to call it without **--pstop** parameter.

```bash
python3 -m athena -n asd -b 60000 40000 --rounds 132 297
A (60000) vs B (40000)
	margin:	0.2

	Approx round schedule:	[132, 297]
	athena kmins:		[75, 165]
	athena pstop cumul (audit):	[0.798620073240586, 0.9604763404354484]
	athena pstop cumul (tied): 	[0.06933400321906029, 0.08488117767255868]
	athena pstop round (audit):	[0.798620073240586, 0.16185626719486235]
	athena pstop round (tied): 	[0.06933400321906029, 0.015547174453498389]
	athena deltas ():	[0.38483741421193757, 0.5336003665053679]
	athena ratio:	[0.08681725584196939, 0.08837404327323288]
```

At the end we may want to check how, for that round schedule Arlo audit would work

```bash
python3 -m athena -n asd -b 60000 40000 --rounds 132 297 --type arlo
A (60000) vs B (40000)
	margin:	0.2

	Approx round schedule:	[132, 297]
	arlo kmins:		[79, 170]
	arlo pstop cumul (audit):	[0.5517707405988952, 0.8681144359578332]
	arlo pstop cumul (tied): 	[0.014585813499702633, 0.01949572249866391]
	arlo pstop round (audit):	[0.5517707405988952, 0.316343695358938]
	arlo pstop round (tied): 	[0.014585813499702633, 0.004909908998961276]
	arlo deltas ():	[0.07601726700482737, 0.07026836102128318]
	arlo ratio:	[0.026434554111860128, 0.02245754901789339]
```

## Wald's sequential test

Wald's sequential test (BRAVO audit) can be seen as a special case of AURROR.
AURROR with round schedule **[1, 2, 3, ..., max]** is the same as Wald's sequential
test that stops after up to **max** ballots checked.

Calling:

```bash
python3 -m athena -n asd -b 6000 4000  --rounds 17 --type BRAVO
```

Is equivalent to calling:

```bash
python3 -m athena -n asd -b 6000 4000  --rounds 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17
```

Note that **athena** uses the code that is optimized for a few rounds of (potentially) large sizes
while BRAVO test has each round of size 1. Therefore you may prefere to run a previous version
of the code:

```
python3 code/aurror_old.py -n asd -b 6000 4000  --rounds 17
```


## Estimating true audit risk

```
python -m athena -n 2016_Minnesota  -b 1367825 1323232  --rounds 14880 32138   --risk 7530


{'2016_Minnesota': {"round_number": 2, "min_kmins": [7531, 0], "risks": [0.10015171727863798]}}

```

## Efficiency vs accuracy

The default method of computing probability distributions uses **scipy.convolve** function with its
default **method='direct'** option. For tight margins audit requires large round sizes. For such a case, a speed up
may be achieved by switching the default  method to **method='direct'**, it is achieved by adding a flag
**--conv fft** to the call.


```
time python -m athena -n Convolve --conv fft --ballots 5050 4950 --rounds 30000 150000 --type minerva 


A (5050) vs B (4950)
	margin:	0.01

	Approx round schedule:	[30000, 150000]
	minerva kmins:		[15139, 75308]
	minerva pstop cumul (audit):	[0.5528304495551454, 0.9902384020897739]
	minerva pstop cumul (tied): 	[0.05488062600183151, 0.0986169006106063]
	minerva pstop round (audit):	[0.5528304495551454, 0.4374079525346285]
	minerva pstop round (tied): 	[0.05488062600183151, 0.043736274608774786]
	minerva deltas ():	[0.2780323883486859, 3.819691573156511]
	minerva ratio:	[0.09927207527369947, 0.09958904886185761]

real	0m7,983s
user	0m8,826s
sys	0m1,028s
```

The speed up is larger as the round sizes grow

```
time python -m athena -n Convolve --conv direct --ballots 5050 4950 --rounds 30000 150000 --type minerva 


A (5050) vs B (4950)
	margin:	0.01

	Approx round schedule:	[30000, 150000]
	minerva kmins:		[15139, 75308]
	minerva pstop cumul (audit):	[0.5528304495551454, 0.9902384020897737]
	minerva pstop cumul (tied): 	[0.05488062600183151, 0.09861690061060624]
	minerva pstop round (audit):	[0.5528304495551454, 0.4374079525346283]
	minerva pstop round (tied): 	[0.05488062600183151, 0.04373627460877473]
	minerva deltas ():	[0.2780323883486859, 3.8196915731565126]
	minerva ratio:	[0.09927207527369947, 0.09958904886185758]

real	0m10,637s
user	0m25,301s
sys	0m15,916s
```

## Help

```
python -m athena -h
```

returns:

```
usage: athena.py [-h] [-v] [-n NEW] [-a ALPHA]
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

## Unit tests

Outside the **code** directory: **pytest-3 code** (or **python -m pytest code**).

Inside the **code** directory: **pytest-3** (or **python -m pytest**)

## Old version BRAVO/ARLO/ATHENA

Previous implementations:

- code/aurror_old.py
- code/aurror.py

were here up to the [following commit](https://github.com/filipzz/athena/commit/ffa135d5f7f9ce842d1fc8ec905e7252797f10b7).

```
python3 aurror_old.py --new raceName --alpha .1 --candidates "Albus D." Bob Cedric --ballots 5000 3000 2000 --round_schedule 100 200
Results of: raceName
Number of valid ballots: 10000
	1 Albus D.	5000
	2 Bob	3000
	3 Cedric	2000

Parameters: 
Alpha:  0.1
Gamma:  1.0
Model:  bin
Round schedule: [100, 200]


Albus D. (5000) vs Bob (3000)
	margin:	0.25

	Effective round schedule: [80, 160]

	BRAVO kmins: 	[50, 95]
	BRAVO risk: 	[0.06235051 0.08209004]
	BRAVO pstop: 	[0.6862955 0.9054928]
	--- ratio:	[0.09085082782119536, 0.09065786273502807]

	ARLO kmins:	[50, 95]
	ARLO risk:	[0.01649631 0.0234236 ]
	ARLO pstop:	[0.54969483 0.83843797]
	--- ratio:	[0.030009940780989588, 0.027937185688492874]

	Athena kmins:	[47, 92]
	Athena risk:	[0.07281773 0.08800107]
	Athena pstop:	[0.79143613 0.93830014]
	--- ratio:	[0.092007080402985, 0.09378776507297898]


Albus D. (5000) vs Cedric (2000)
	margin:	0.42857142857142855

	Effective round schedule: [70, 140]

	BRAVO kmins: 	[46, 89]
	BRAVO risk: 	[0.07876542 0.08264516]
	BRAVO pstop: 	[0.95085346 0.99592736]
	--- ratio:	[0.08283654763927709, 0.08298311619828014]

	ARLO kmins:	[46, 89]
	ARLO risk:	[0.0057632  0.00623018]
	ARLO pstop:	[0.88184075 0.98651178]
	--- ratio:	[0.006535425834876662, 0.006315362816084122]

	Athena kmins:	[41, 83]
	Athena risk:	[0.0941081  0.09882721]
	Athena pstop:	[0.99258982 0.99961812]
	--- ratio:	[0.0948106654177994, 0.09886496664859996]


Bob (3000) vs Cedric (2000)
	margin:	0.2

	Effective round schedule: [50, 100]

	BRAVO kmins: 	[34, 61]
	BRAVO risk: 	[0.02323915 0.05373822]
	BRAVO pstop: 	[0.25028037 0.5834069 ]
	--- ratio:	[0.0928524486015076, 0.09211103820218584]

	ARLO kmins:	[34, 61]
	ARLO risk:	[0.00767334 0.02212395]
	ARLO pstop:	[0.1560906  0.47770637]
	--- ratio:	[0.04915951815417218, 0.04631285308993794]

	Athena kmins:	[32, 59]
	Athena risk:	[0.03245432 0.0627022 ]
	Athena pstop:	[0.33561326 0.65119262]
	--- ratio:	[0.09670155223011023, 0.0962882608728027]
```


# Acknowledgements

We thank [NSF (1421373 TWC: TTP Option: Small: Open-Audit Voting Systems---Protocol Models and Properties)](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1421373) for funding the implementation of this project.
