# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 16:16:39 2020

@author: windows
"""

import pandas as pd
import pickle
import sys
import os
curdir = os.getcwd()
while 'filepathhelper.py' not in os.listdir(curdir):
        curdir = os.path.dirname(curdir)
sys.path.append(curdir)
import filepathhelper

def issueContribution(userlog, changelog):
    print()


if __name__== "__main__":
  
    if len(sys.argv) == 2:   
        dataset = sys.argv[1]
        if dataset == 'Moodle':
            changelog = pd.read_csv(filepathhelper.path(dataset,'changelog.csv'), sep = ';')
            developer = pd.read_csv(filepathhelper.path(dataset,'developer.csv'))
            tester = pd.read_csv(filepathhelper.path(dataset,'tester.csv'))
            reviewer = pd.read_csv(filepathhelper.path(dataset,'peer_reviewer.csv'))
            integrator = pd.read_csv(filepathhelper.path(dataset,'integrator.csv'))
            
            developer = set(developer['username'])
            tester = set(tester['username'])
            reviewer = set(reviewer['username'])
            integrator = set(integrator['username'])
            
            person = developer.union(tester, reviewer)
            person = person.union(integrator)
            
        elif dataset == 'Apache':
            changelog = pd.read_csv(filepathhelper.path(dataset,'changelog.csv'), sep = ';',error_bad_lines=False,low_memory=False)
            person = pd.read_csv(filepathhelper.path(dataset,'uniqueusername.csv'))
        person = person['username']
        loggroup = changelog.groupby(['username']).groups
        userlog = changelog['username']

        activity = []
        for p in person:
            print(p)
            if p in list(userlog):
                acttime = []
                for i in loggroup[p]:
                    print(p, i)
                    acttime.append({'issuekey': changelog.loc[i]['issuekey'],'time':changelog.loc[i]['timecreated']})
                activity.append({'username':p, 'timeact': acttime})
        print('done')
        name = "useractivity_"+dataset+".p"
        pickle.dump( activity, open( name, "wb" ) )