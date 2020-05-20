# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 16:16:39 2020

@author: windows
"""

import pandas as pd
import pickle
import sys
import os
import json
from tqdm import tqdm
import datetime as dt

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


if __name__== "__main__":
    if 1>0:
#    if len(sys.argv) == 2:   
#        dataset = sys.argv[1]
#        print(dataset)
        changelog = pd.read_csv(filepathhelper.path(dataset,'changelog.csv'), sep = ';')
        with open(filepathhelper.path(dataset,'rp'),'rb') as f:
            rp=pickle.load(f)
        person = set()
        for i in rp:
            person.update(rp[i])

        loggroup = changelog.groupby(['username']).groups
        userlog = set(changelog['username'])
        print('finish reading files')
        activity = {}
        for p in tqdm(person):
            if p in userlog:
                acttime = set()
                for i in loggroup[p]:
                    act = changelog.loc[i]
                    #print(p, i)
                    acttime.add((act['issuekey'],dt.datetime.strptime(act['timecreated'], '%Y-%m-%d %H:%M:%S')))
                activity[p] = acttime
        print('done')
            
        pickle.dump( activity, open(filepathhelper.path(dataset,"useractivity.p"), "wb" ) )