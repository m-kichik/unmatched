**Installation**:

`git clone https://github.com/m-kichik/unmatched/`

`python3 -m pip install -r requirements.txt`

**Tools**:

- _Generate sample_:
  Simple script for generating 2, 3 or 4 heroes sample and a map. It is started by the command:

  `python3 generate_sample.py [configuration file] [number of players] [sampling policy]`

  Where arguments are:
  - Configuration file is a .yaml file that has the same structure with
    [sets_configs/sets.yaml](https://github.com/m-kichik/unmatched/blob/main/sets_configs/sets.yaml). Heroes and map are sampling randomly with probabilities
    proportional to SET_WEIGHT * hero|map value (the number from configuration file);
  - Number of players is literally a number (2, 3 or 4);
  - Sampling policy is one of "w" (from weighted) or "s" (from statistical).
 
  So the typical command for generating will look like:

  `python3 generate_sample.py sets_configs/sets.yaml 2 w`

  _"Statistical" policy explanation._
  In this case [information from the UmDb](https://unmatched.cards/results) is used. The first hero (or a pair of heroes in case of 4-players mode)
  is selected randomly from the full list of heroes. The second hero (or a pair, or next two heroes in case of 3-players mode) is also selected randomly
  with respect to some probabilities. These probabilities are computed using winrates of the previously selected hero VS other heroes. Since the goal is to make
  balanced sample, winrates close to 0.5 are preferred. To reward such winrates a special function f(x) is used: it takes winrate as x and returns probability,
  which is supposed to be relatively big if x is close to 0.5 and small otherwise. This f(x) is normal distribution with &mu; = 0.5. The following picture shows
  such distribution for different paramaters &sigma;:
  
  ![Normal distribution](https://github.com/m-kichik/unmatched/blob/main/media/normal.png)

  This illustrates the impact of the parameter &sigma;. If it is quite big, e.g. 0.2, we have relatively big probabilities for such winrates as 0.3 and 0.75, which
  means, that the resulting sample may be imbalanced. Otherwise, if &sigma; is small, e.g. 0.1, we reward only "balanced" winrates and this makes variability
  of our samples worse.
  
