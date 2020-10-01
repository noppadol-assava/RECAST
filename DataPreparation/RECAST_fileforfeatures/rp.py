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
issuecomponent = pd.read_csv(filepathhelper.path(dataset,'component_title.csv'),sep=';;;',engine='python')

teams = teams[(teams['issuekey'].isin(closeresolve['issuekey']))]
assignees = assignees[(assignees['issuekey'].isin(teams['issuekey']))]
teams = teams[teams['issuekey'].isin(trainset['issuekey'])]
assignees = assignees[assignees['issuekey'].isin(trainset['issuekey'])]
winissues = winissues[winissues['issuekey'].isin(trainset['issuekey'])]

dev = list(teams['dev'].unique())
tmp = []
for i in dev:
    if str(i) !='nan':
        tmp.append(i)
dev = tmp

test = list(teams['tester'].unique())
tmp = []
for i in test:
    if str(i) !='nan':
        tmp.append(i)
test = tmp

peer = list(teams['peer'].unique())
tmp = []
for i in peer:
    if str(i) !='nan':
        tmp.append(i)
peer = tmp


integrator = list(teams['integrator'].unique())
tmp = []
for i in integrator:
    if str(i) !='nan':
        tmp.append(i)
integrator = tmp


rp = {'dev':dev,'test':test,'peer':peer,'integrator':integrator}

with open(filepathhelper.path(dataset,'rp'),'wb') as f:
    pickle.dump(rp,f)