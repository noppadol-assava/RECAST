# Comment sentiment analysis

This section involves sentiment analysis of comments in each issues

## How to run code

### Preparation

In this section, SentiStrength was used to analyze text. Since sentistrength is lexicon based text analysis, it requires dictionary as in folder 'resource'

* It requires installation of sentistrength library in python
* SentiStrength was used to analyze text. Since sentistrength is lexicon based text analysis, it requires dictionary as in folder 'sentistrength'
* Move all files in sentistrength python library
* Change path of the sentistrength library
* Input is required in data and output is in sentiout directory

```
senti = PySentiStr()
senti.setSentiStrengthPath('.../lib/python2.7/site-packages/sentistrength/SentiStrength.jar')
senti.setSentiStrengthLanguageFolderPath('.../lib/python2.7/site-packages/sentistrength/')

```

### Run code
* Change path of input and output files
```
commentFile = '.../data/Moodle_comments.csv'
tagPair = '.../data/tags.csv'
logFile = 'sentiout/logfile.txt'
output_score = '.../sentiout/score1.csv'
output_invalid = '.../sentiout/invalid1.csv'

```
* Run file by using this command
```
python sentiment_token.py
```

### Get team interaction score
* call function in teamInteractionScore.py
```
team_interaction_score(dataset, global_pair_score_fileName, team)
```
* Run whole file
```
python teamInteractionScore.py Moodle global_pair_score_Moodle.csv
```
team must have this structure
```
team = {"developer": [], "integrator": ["jleyva"], "tester": ["jleyva"], "reviewer": ["dpalou"], "assignee": ["fred"]}
```
