# Evaluation

## Team recommendation Evaluation
This section involves evaluation of team recommendation, which consists of this following evaluation metrics:
* MRR
* Mean Rank of Hits
* Mean Rank
* Hit at 10
* Hit at 100
* Bpref
* MAP
* Precision at K

This evaluation metrics are applied differently to this following evalution protocols:
* Exact Match
* Half Match
* Partial Match


### Run code
To use this evaluation code, use this command in command line
```
python evaluation_final.py mode actualResult.json recommendResult.json output.txt

```
There are 4 evaluation modes you could use
* allMatch (exactMatch, halfMatch, partialMatch)
* exactMatch
* halfMatch
* partialMatch

```
python evaluation_final.py allMatch actual_team_file.json recommend_output.json evaluation_result.txt

```
* Run file by using this command
```
python evaluation_final.py allMatch actual//actual.json out//recommendResult.json eval.txt
```

## Individual recommendation Evaluation
This section involves evaluation of individual team member.

### Run code
Use function `allApproachSingleRoleEvaluation()` to evaluate role by role and `allApproachEvaluation()` to evaluate all roles
```
allApproachEvaluation(datasetName, outputFilePath)
allApproachSingleRoleEvaluation('datasetName', outputFilePath)
```