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

PtoI={}
for key,issue in tqdm(teams.iterrows(),total=teams.shape[0]):
    dev = issue['dev'] if str(issue['dev'])!='nan' else None
    inte = issue['integrator'] if str(issue['integrator'])!='nan' != '\\N' else None
    peer = issue['peer'] if str(issue['peer'])!='nan' else None
    test = issue['tester'] if str(issue['tester'])!='nan' else None
    if dev not in PtoI and dev is not None:
        PtoI[dev] = set()
    if inte not in PtoI and inte is not None:
        PtoI[inte] = set()
    if peer not in PtoI and peer is not None:
        PtoI[peer] = set()
    if test not in PtoI and test is not None:
        PtoI[test] = set()
		
    if dev is not None:
        PtoI[dev].add(issue['issuekey'])
    if inte is not None:
        PtoI[inte].add(issue['issuekey'])
    if peer is not None:
        PtoI[peer].add(issue['issuekey'])
    if test is not None:
        PtoI[test].add(issue['issuekey'])
    
for key,issue in tqdm(assignees.iterrows(),total=assignees.shape[0]):
    assignee = issue['username']
    if assignee not in PtoI:
        PtoI[assignee] = set()
    PtoI[assignee].add(issue['issuekey'])

with open(filepathhelper.path(dataset,'PtoI'),'wb') as f:
    pickle.dump(PtoI,f)