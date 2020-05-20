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
import re
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
        team[issuekey].add(dev)
    if inte is not None:
        team[issuekey].add(inte)
    if peer is not None:
        team[issuekey].add(peer)
    if test is not None:
        team[issuekey].add(test)
    team[issuekey].add(assignee)


ProjExp={}
for issuekey in tqdm(team):
    proj = re.match(r"(.*?)-", issuekey).group(1)
    for p in team[issuekey]:
        if p not in ProjExp:
            ProjExp[p]={}
        ProjExp[p][proj] = 1 if proj not in ProjExp[p] else ProjExp[p][proj]+1

    

with open(filepathhelper.path(dataset,'ProjExp'),'wb') as f:
    pickle.dump(ProjExp,f)