import os
import sys
import json

curdir = os.getcwd()
while 'config.json' not in os.listdir(curdir):
    curdir = os.path.dirname(curdir)
with open(os.path.join(curdir,'config.json'), 'r') as f:
    dataset = json.load(f)['dataset']

curdir = os.getcwd()
while 'filepathhelper.py' not in os.listdir(curdir):
       curdir = os.path.dirname(curdir)
sys.path.append(curdir)
import filepathhelper

import math
import random
import pandas as pd
import numpy as np
from tqdm import tqdm
import pickle
#from tqdm import tqdm_notebook as tqdm


teams = pd.read_csv(filepathhelper.path(dataset,'team.csv'))
closeresolve = pd.read_csv(filepathhelper.path(dataset,'closeresolve.csv'),sep=';')
winissues = pd.read_csv(filepathhelper.path(dataset,'winissue.csv'))
assignees = pd.read_csv(filepathhelper.path(dataset,'assignee.csv'),sep=';')
trainset = pd.read_csv(filepathhelper.path(dataset,'trainissuekey.csv'))

teams = teams[(teams['issuekey'].isin(closeresolve['issuekey']))]
assignees = assignees[(assignees['issuekey'].isin(teams['issuekey']))]
teams = teams[teams['issuekey'].isin(trainset['issuekey'])]
assignees = assignees[assignees['issuekey'].isin(trainset['issuekey'])]
winissues = winissues[winissues['issuekey'].isin(trainset['issuekey'])]
assignees.set_index('issuekey',inplace=True)

username = set()
team = {}
for key,issue in tqdm(teams.iterrows(),total=teams.shape[0]):
    issuekey = issue['issuekey']
    if issuekey not in team:
        team[issuekey] = set()
    assignee = assignees.loc[issuekey]['username']
    dev = issue['dev'] if str(issue['dev'])!='nan' else None
    inte = issue['integrator'] if str(issue['integrator'])!='nan' != '\\N' else None
    peer = issue['peer'] if str(issue['peer'])!='nan' else None
    test = issue['tester'] if str(issue['tester'])!='nan' else None
    if dev is not None:
        username.add(dev)
        team[issuekey].add(dev)
    if inte is not None:
        username.add(inte)
        team[issuekey].add(inte)
    if peer is not None:
        username.add(peer)
        team[issuekey].add(peer)
    if test is not None:
        username.add(test)
        team[issuekey].add(test)
    username.add(assignee)
    team[issuekey].add(assignee)

worktogether = {}
for i in username:
    for j in username:
        if i != j:
            if i not in worktogether:
                worktogether[i] = {}
            worktogether[i][j] = 0

for issuekey in team:
    t = team[issuekey]
    for i in t:
        for j in t:
            if i!=j:
                worktogether[i][j]=worktogether[i][j]+1
                worktogether[j][i]=worktogether[j][i]+1

with open(filepathhelper.path(dataset,'worktogether'),'wb') as f:
    pickle.dump(worktogether,f)