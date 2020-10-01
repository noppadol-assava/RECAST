# to run python haibin_form.py ../Train_Test_data/moodle/input_moodle_train.json out/moodle_train.json
#!/usr/bin/env python
# coding: utf-8

# In[5]:


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
import numpy as np
import pandas as pd
from tqdm import tqdm
import pickle

with open(filepathhelper.path(dataset,'haibin/ptonum'),'rb') as f:
    ptonum=pickle.load(f)
with open(filepathhelper.path(dataset,'haibin/roleexp_dev'),'rb') as f:
    roleexp_dev=pickle.load(f)
with open(filepathhelper.path(dataset,'haibin/roleexp_integrator'),'rb') as f:
    roleexp_integrator=pickle.load(f)
with open(filepathhelper.path(dataset,'haibin/roleexp_peer'),'rb') as f:
    roleexp_peer=pickle.load(f)
with open(filepathhelper.path(dataset,'haibin/roleexp_test'),'rb') as f:
    roleexp_test=pickle.load(f)
with open(filepathhelper.path(dataset,'haibin/roleexp_assignee'),'rb') as f:
    roleexp_assignee=pickle.load(f)
with open(filepathhelper.path(dataset,'haibin/experience'),'rb') as f:
    experience=pickle.load(f)
with open(filepathhelper.path(dataset,'haibin/winexp'),'rb') as f:
    winexp=pickle.load(f)
with open(filepathhelper.path(dataset,'haibin/winrate'),'rb') as f:
    winrate=pickle.load(f)
with open(filepathhelper.path(dataset,'haibin/workadj'),'rb') as f:
    workadj=pickle.load(f)
with open(filepathhelper.path(dataset,'haibin/tagadj'),'rb') as f:
    tagadj=pickle.load(f)
with open(filepathhelper.path(dataset,'haibin/weight'),'rb') as f:
    weight=pickle.load(f)

tags = pd.read_csv(filepathhelper.path(dataset,'tags.csv'),encoding = 'ISO-8859-1')
teams = pd.read_csv(filepathhelper.path(dataset,'team.csv'))
closeresolve = pd.read_csv(filepathhelper.path(dataset,'closeresolve.csv'),sep=';')
teams = teams[(teams['issuekey'].isin(closeresolve['issuekey']))]
winissues = pd.read_csv(filepathhelper.path(dataset,'winissue.csv'))
assignees = pd.read_csv(filepathhelper.path(dataset,'assignee.csv'),sep=';')
assignees = assignees[(assignees['issuekey'].isin(teams['issuekey']))]

trainset = pd.read_csv(filepathhelper.path(dataset,'trainissuekey.csv'))
teams = teams[teams['issuekey'].isin(trainset['issuekey'])]
assignees = assignees[assignees['issuekey'].isin(trainset['issuekey'])]
winissues = winissues[winissues['issuekey'].isin(trainset['issuekey'])]

issuecomment = pd.read_csv(filepathhelper.path(dataset,'issuekey_comments.csv'),sep=';')
issuecomment = issuecomment[issuecomment['issuekey'].isin(trainset['issuekey'])]
tags = tags[tags['commentid'].isin(issuecomment['commentid'])]

allpp = set(teams['dev'].unique())
allpp.update(tags['tagger'].unique())
allpp.update(tags['taggee'].unique())
allpp.update(teams['tester'].unique())
allpp.update(teams['peer'].unique())
allpp.update(teams['integrator'].unique())
allpp.update(assignees['username'].unique())

# {dev:A,dev2:A2,integrator:B,peer:C,tester:D}
def teamStrengthCost(Team):
    team = set()
    e=0
    we=0
    wr=0
    re=0
    cl=0
    cn=0
    countrole = 0
    for i in Team:
        if Team[i] not in ptonum:
            countrole=countrole+1
            continue
        num = ptonum[Team[i]]
        team.add(num)
        if(i.startswith('dev')):
            re = re + roleexp_dev[num]
        elif(i.startswith('integrator')):
            re = re + roleexp_integrator[num]
        elif(i.startswith('peer')):
            re = re + roleexp_peer[num]
        elif(i.startswith('tester')):
            re = re + roleexp_test[num]
        elif(i=='assignee'):
            re = re + roleexp_assignee[num]   
        e = e + experience[num]
        we = we + winexp[num]
        wr = wr + winrate[num]
        countrole=countrole+1
    re = re/countrole
    e = e/countrole
    we = we/countrole
    wr = wr/countrole
    if len(team)>1:
        teamlis = list(team)
        for i in range(len(teamlis)):
            for j in range(i+1,len(teamlis)):
                p1 = teamlis[i]
                p2 = teamlis[j]
                if workadj[p1][p2]==math.inf:
                    cl = cl+1/len(allpp)
                else:
                    cl = cl+1/workadj[p1][p2]
                cn = cn+tagadj[p1][p2]
        cl = cl*2/len(teamlis)/(len(teamlis)-1)
        cn = cn*2/len(teamlis)/(len(teamlis)-1)

#atlassian    teamstrength = wr*4.071075 +cn*5.095597 -3.109049
#atlassian_hitnohit    teamstrength = e*1.229703 + wr*1.257710 + re*4.568270 + cl*5.496494 + cn*2.870109 -10.118352
#apache    teamstrength = we*0.03983085+wr*8.57685950 -5.41508818
#apache_hitnohit    teamstrength = e*5.234990 + re*5.862321 + cl*4.213768 + cn*4.560076 - 6.370337
#moodle    teamstrength = 0.4542186*e+9.5260501*wr-6.5136572
#moodle_hitnohit    teamstrength = e*3.4240299+wr*1.4762039+re*8.8590164+cl*0.6242984+cn*23.1703404-8.6098744
#    teamstrength = e*weight['experience']+we*weight['winexperience']+wr*weight['winrate']+re*weight['roleexperience']+cl*weight['closeness']+cn*weight['connection']+weight['intercept']
    return 1/teamstrength if teamstrength>0 else math.inf



