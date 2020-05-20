# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 16:02:55 2020

@author: windows
"""

import pandas as pd
import os
import sys
import json
import pickle
from tqdm import tqdm

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



def generateContributionFile():
    changelog = pd.read_csv(filepathhelper.path(dataset,"changelog.csv"),quotechar='"', sep = ';')
    with open(filepathhelper.path(dataset,'rp'),'rb') as f:
        rp=pickle.load(f)

    train = pd.read_csv(filepathhelper.path(dataset,"trainissuekey.csv"))   
    #select only changelog in in 
    changelog = changelog[changelog.issuekey.isin(train.issuekey)][['issuekey','username']]
    
    
    user = set()
    for i in rp:
        user .update(rp[i])

    
    lognamegroup = changelog.groupby(['username']).groups
    logkeygroup = changelog.groupby(['issuekey']).count()
    
    
    person = set(changelog['username'])
    user = list(user)
    
    username = []
    contribution = []
    
    for i in tqdm(range(len(user))):
        activity = []
        if user[i] in person:
            loglist = changelog[changelog['username']==user[i]]
            logcount = loglist.groupby(['issuekey']).count().reset_index()
            
            for index, row in logcount.iterrows():
                activity.append(row['username']/logkeygroup.loc[row['issuekey']].values[0])
                
            username.append(user[i])
            contribution.append(sum(activity) / len(activity))
    
                
    d = {'username':username, 'contribution':contribution }
    df = pd.DataFrame(data = d)
    df.to_csv(filepathhelper.path(dataset,'contribution.csv'))

generateContributionFile()