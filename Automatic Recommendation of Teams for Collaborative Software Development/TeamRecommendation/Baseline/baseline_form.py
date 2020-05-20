# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 16:45:40 2019

@author: windows
"""


import os
import sys
import json

curdir = os.getcwd()
while 'filepathhelper.py' not in os.listdir(curdir):
       curdir = os.path.dirname(curdir)
sys.path.append(curdir)
import filepathhelper

import sys

import BaselineUtility
import pandas as pd
import sys
import math
import random
import multiprocessing as mp
from tqdm import tqdm
import pickle
import hashlib

dataset = BaselineUtility.dataset
# from tqdm import notebook_tqdm as tqdm

def hash_team(team):
    t_sorted = {i:sorted(team[i]) if type(team[i]) == list else team[i] for i in team}
    ## hash team
    t_hash = hashlib.sha1(json.dumps(t_sorted, sort_keys=True).encode()).hexdigest()
    return t_hash

allteam_cache = {}
def maxlogit(N,roles_pp,alpha,cost,context='',component='',issuekey=''):
    allteam = []#tor add
    if individual:
        roles = [missingrole]
    else:
        roles = [r for r in roles_pp] 
        roles.remove('assignee') # not random assignee
    
    T = {roles_pp[0]:random.choice(roles_pp[1]) for roles_pp in roles_pp.items()} #1
    bestT=T #1
    if issuekey!='':
        cb = cost(bestT)
    else:
        cb = cost(bestT)
        
    allteam_cache[hash_team(bestT)] = cb # tor add
    allteam.append((bestT,cb)) # tor add
    
    for i in range(1,N): #2
#     if N > 0:
        hashT = hash_team(T) #tor add
        c = cost(T) if hashT not in allteam_cache else allteam_cache[hashT] #3 tor modified
        Tp = T.copy() #4
        randomrole = random.choice(roles) #4 modified by tor (not change assignee)
        Tp[randomrole] = random.choice(roles_pp[randomrole]) #4
        
        # tor modified if team has been calculated before don't re calculate
        hashTP = hash_team(Tp)
        
        cp = cost(Tp) if hashTP not in allteam_cache else allteam_cache[hashTP] #5 tor modified

        allteam.append((Tp,cp)) # tor add
        allteam_cache[hashTP] = cp #tor add
        
        prob = probability(c,cp,alpha) #6
        r = random.uniform(0, 1) #7
        if r <= prob:#8
            T = Tp #9
            c = cp #9
#             allteam.append((T,c)) # tor add
            if c < cb: #10
                bestT = T #11
                cb = c #11
#                 allteam.append((bestT,cb)) # tor add
#     return bestT,cb
    return allteam # tor modified

def probability(costT,costTp,alpha): #16
    try:
        vt = math.exp(-costT/alpha) #17
    except OverflowError:
        vt = math.inf if costT<0 else 0
    try:
        vtp = math.exp(-costTp/alpha) #18
    except OverflowError:
        vtp = math.inf if costTp<0 else 0
    if max(vt,vtp) !=0:
        prob = vtp/max(vt,vtp) #19
    else:
        prob = 1
    return prob #20



def format_output(team,rank):
    
    # filter out all duplicate team
    hashteam = set()
    temp = []
    for t,s in team:
        t_sorted = {i:sorted(t[i]) if type(t[i]) == list else t[i] for i in t}
        ## hash team
        t_hash = hashlib.sha1(json.dumps(t_sorted, sort_keys=True).encode()).hexdigest()
        if t_hash not in hashteam:
            hashteam.add(t_hash)
            temp.append((t,s))
    team = temp
    team = team[:min(len(team),rank)]
    rank = []
    rankno=1
    team.sort(key=lambda tup: tup[1]) 
    for team,score in team:
        rankdict = {'rank':rankno,'team':{'developer':[],'integrator':[],'tester':[],'reviewer':[],'assignee':[]}}
        for r in team:
            if r =='assignee':
                rankdict['team']['assignee'].append(team[r])
            elif r.startswith('dev'):
                rankdict['team']['developer'].append(team[r])
            elif r.startswith('integrator'):
                rankdict['team']['integrator'].append(team[r])
            elif r.startswith('peer'):
                rankdict['team']['reviewer'].append(team[r])
            elif r.startswith('tester'):
                rankdict['team']['tester'].append(team[r])
        rank.append(rankdict)
        rankno=rankno+1
    return rank

def saveOutput(outname):
    outdata = result
#    outfile = 'out\\'+outname+'.json'
    outfile = outname
    with open(outfile, 'w') as outfile:
        json.dump(outdata, outfile)
def teamrec(p):
    if 1>0:
        if 1>0:
            if 1>0:
                rp_temp = {}
                rp_temp['assignee'] = [p['assignee']]
                # assign candidates to each roles
                if individual:
                    availableFlag = False
                    actualTeam = actual.loc[p['issuekey']]['r'][0]['team']
                    countDev=0
                    countRev=0
                    countTes=0
                    countInt=0
                    for j in p['team']:
                        if(j.startswith(missingrole)):
                            rp_temp[j] = rp[missingrole[:-1]] if missingrole != 'tester1' else rp['test']
                            availableFlag = True
                        elif(j.startswith('dev')):
                            rp_temp[j] = [actualTeam['developer'][countDev]]
                            countDev=countDev+1
                        elif(j.startswith('integrator')):
                            rp_temp[j] = [actualTeam['integrator'][countInt]]
                            countInt=countInt+1
                        elif(j.startswith('peer')):
                            rp_temp[j] = [actualTeam['reviewer'][countRev]]
                            countRev=countRev+1
                        elif(j.startswith('tester')):
                            rp_temp[j] = [actualTeam['tester'][countTes]]
                            countTes=countTes+1
                else:
                    for j in p['team']:
                        if(j.startswith('dev')):
                            rp_temp[j] = rp['dev']
                        elif(j.startswith('integrator')):
                            rp_temp[j] = rp['integrator']
                        elif(j.startswith('peer')):
                            rp_temp[j] = rp['peer']
                        elif(j.startswith('tester')):
                            rp_temp[j] = rp['test']
                #Get recommend team
                if individual:
                    if availableFlag:
                        team = maxlogit(1000,rp_temp,0.05,Oneline.teamStrengthCost)
                        team = format_output(team,RANK)
                        return {'issue': p['issuekey'], 'r': team} 
                    else:
                        return None
                else:
                    team = maxlogit(1000,rp_temp,0.05,Oneline.teamStrengthCost)
                    team = format_output(team,RANK)
                    return {'issue': p['issuekey'], 'r': team}
        
                                 
if __name__== "__main__":
    NUMTHREAD=25
    inputname = filepathhelper.path(dataset,'input_test.json')
    random.seed(123)
    outdata = {} 
    RANK=100
    result = []
    with open(filepathhelper.path(dataset,'rp'),'rb') as f:
        rp = pickle.load(f)
    if len(sys.argv) == 2: 
        outputname = sys.argv[1]
        individual = False
    elif len(sys.argv) == 3:
        outputname = sys.argv[1]
        individual = True
        missingrole = sys.argv[2]+str('1')
    else:
        inputname = 'input\\input2.json'
        outputname = 'out\\recommendResult.json'
        individual = False

    if individual:
        with open(filepathhelper.path(dataset,'actual_team.json')) as json_file:
            actual = pd.DataFrame(json.load(json_file))
            actual.set_index('issue',inplace=True)
            
            
    with open(inputname) as json_file:
        data = json.load(json_file)
        with mp.Pool(NUMTHREAD) as p:
            multi_out = tqdm(p.imap(teamrec,data,chunksize=1),total=len(data))
            temp = [i for i in multi_out]
        result = []
        for i in temp:
            if i is not None:
                result.append(i)
        #save to json file
        saveOutput(outputname)    
         
