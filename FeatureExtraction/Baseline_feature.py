#!/usr/bin/env python
# coding: utf-8

# In[ ]:


NUMTHREAD = 15


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
# from tqdm import tqdm
import pickle
from tqdm import tqdm_notebook as tqdm
import multiprocessing as mp


# In[ ]:


from numpy import newaxis,minimum
def warshall(mat):
    n = len(mat)
    for k in tqdm(range(n)):
        mat = minimum(mat, mat[newaxis,k,:] + mat[:,k,newaxis]) 

    return mat


# In[ ]:


tags = pd.read_csv(filepathhelper.path(dataset,'tags.csv'),encoding = 'ISO-8859-1')
teams = pd.read_csv(filepathhelper.path(dataset,'team.csv'))
closeresolve = pd.read_csv(filepathhelper.path(dataset,'closeresolve.csv'),sep=';')
teams = teams[(teams['issuekey'].isin(closeresolve['issuekey']))]
winissues = pd.read_csv(filepathhelper.path(dataset,'winissue.csv'))
assignees = pd.read_csv(filepathhelper.path(dataset,'assignee.csv'),sep=';')
assignees = assignees[(assignees['issuekey'].isin(teams['issuekey']))]

# assignees.shape
# assignees.head()
# closeresolve.head()


# # train on only train dataset

# In[ ]:


trainset = pd.read_csv(filepathhelper.path(dataset,'trainissuekey.csv'))
teams = teams[teams['issuekey'].isin(trainset['issuekey'])]
assignees = assignees[assignees['issuekey'].isin(trainset['issuekey'])]
winissues = winissues[winissues['issuekey'].isin(trainset['issuekey'])]

issuecomment = pd.read_csv(filepathhelper.path(dataset,'issuekey_comments.csv'),sep=';')
issuecomment = issuecomment[issuecomment['issuekey'].isin(trainset['issuekey'])]
tags = tags[tags['commentid'].isin(issuecomment['commentid'])]


# In[ ]:


assignees.set_index('issuekey',inplace=True)


# In[ ]:


issuecomment.head()


# # Tor test

# In[ ]:


allpp = set(teams['dev'].unique())
# allpp.update(tags['tagger'].unique())
# allpp.update(tags['taggee'].unique())
allpp.update(teams['tester'].unique())
allpp.update(teams['peer'].unique())
allpp.update(teams['integrator'].unique())
allpp.update(assignees['username'].unique())


# In[ ]:


ttrainset = set(allpp)


# In[ ]:


ttestset = set(allpp)


# # End Tor test

# In[ ]:


teams['result'] =  ['Win' if i==True else 'NotWin' for i in teams['issuekey'].isin(winissues['issuekey'])]


# In[ ]:


teams.head()


# In[ ]:


allpp = set(teams['dev'].unique())
# allpp.update(tags['tagger'].unique())
# allpp.update(tags['taggee'].unique())
allpp.update(teams['tester'].unique())
allpp.update(teams['peer'].unique())
allpp.update(teams['integrator'].unique())
allpp.update(assignees['username'].unique())


# In[ ]:


taggg = set(tags['tagger'].unique())
taggg.update(tags['taggee'].unique())


# In[ ]:


tagadj =  [[0 for x in range(len(allpp))] for y in range(len(allpp))]
# [[0]*len(allpp)]*len(allpp)
workadj =  [[math.inf for x in range(len(allpp))] for y in range(len(allpp))]
for i in range(len(allpp)):
    workadj[i][i]=0
# [[math.inf]*len(allpp)]*len(allpp)
ptonum = {}
count = 0
for p in allpp:
    ptonum[p]=count
    count=count+1
# workadj =  {p:set() for p in allpp}
experience = [0 for x in range(len(allpp))]
winexp = [0 for x in range(len(allpp))]
winrate = [0 for x in range(len(allpp))]
# roleexp = [{'tester':0,'integrator':0,'dev':0,'peer':0} for x in range(len(allpp))] 
roleexp_test = [0 for x in range(len(allpp))]
roleexp_dev = [0 for x in range(len(allpp))]
roleexp_integrator = [0 for x in range(len(allpp))]
roleexp_peer = [0 for x in range(len(allpp))]
roleexp_assignee = [0 for x in range(len(allpp))]
featuretonormalize = {"experience","winexp","roleexp_test","roleexp_dev","roleexp_integrator","roleexp_peer","roleexp_assignee"}


# In[ ]:


teamdict = {}
for key,issue in tqdm(teams.iterrows(),total=teams.shape[0]):
#     print(str(issue['dev'])=='nan')
    issuekey = issue['issuekey']
    team = set()
    if str(issue['dev'])!='nan':
        num = ptonum[issue['dev']]
#         roleexp[num]['dev']=roleexp[num]['dev']+1
        roleexp_dev[num] = roleexp_dev[num]+1
        team.add(num)
    if str(issue['integrator'])!='nan':
        num = ptonum[issue['integrator']]
#         roleexp[num]['integrator']=roleexp[num]['integrator']+1
        roleexp_integrator[num] = roleexp_integrator[num]+1
        team.add(num)
    if str(issue['peer'])!='nan':
        num = ptonum[issue['peer']]
#         roleexp[num]['peer']=roleexp[num]['peer']+1
        roleexp_peer[num] = roleexp_peer[num]+1
        team.add(num)
    if str(issue['tester'])!='nan':
        num = ptonum[issue['tester']]
#         roleexp[num]['tester']=roleexp[num]['tester']+1
        roleexp_test[num] = roleexp_test[num]+1
        team.add(num)
    asn = assignees.loc[issuekey]
    if asn is not None:
        nam = asn['username']
        if str(nam)!='nan':
            num = ptonum[nam]
            roleexp_assignee[num] = roleexp_assignee[num]+1
            team.add(num)
    if issuekey in teamdict:
        teamdict[issuekey][0].update(team)
    else:
        teamdict[issuekey]=[team,issue['result']]
    


# In[ ]:


for t in tqdm(teamdict):
    team = teamdict[t]
    for num in team[0]:
        experience[num] = experience[num]+1
        if team[1] == 'Win':
            winexp[num] = winexp[num]+1
    if len(team[0])>1:
        teamlis = list(team[0])
        for i in range(len(teamlis)):
            for j in range(len(teamlis)):
                nump1 = teamlis[i]
                nump2 = teamlis[j]
                if nump1!=nump2:
                    if workadj[nump2][nump1] == math.inf:
                        workadj[nump2][nump1] = workadj[nump1][nump2] = 0
                    workadj[nump2][nump1]=workadj[nump1][nump2]=workadj[nump1][nump2]+1 
#                     workadj[nump2][nump1]=workadj[nump1][nump2]=1 



# In[ ]:


for i in range(len(allpp)):
    if experience[i]==0:
        winrate[i]=0
    else:
        winrate[i]=winexp[i]/experience[i]


# In[ ]:


featuretonormalize


# In[ ]:


#normalize
def normalize(feature):
    feature = np.array(feature)
    feature = (feature-feature.min())/(feature.max()-feature.min())
    return feature


# In[ ]:


experience = normalize(experience)
winexp = normalize(winexp)
roleexp_test = normalize(roleexp_test)
roleexp_dev = normalize(roleexp_dev)
roleexp_integrator = normalize(roleexp_integrator)
roleexp_peer = normalize(roleexp_peer)
roleexp_assignee = normalize(roleexp_assignee)


# In[ ]:


from scipy.sparse.csgraph import floyd_warshall,shortest_path
workadj = np.array([np.array(xi) for xi in workadj])
tempworkadj = workadj.copy()
workadj[(workadj!=0)&(workadj!=math.inf)]=1


# In[ ]:


workadj,predes = floyd_warshall(workadj,return_predecessors=True)


# In[ ]:


def pathtracking(predecessors,startnode,endnode):
    path = []
    i = endnode
    while i != startnode:
        path.append(i)
        i = predecessors[startnode, i]
    path.append(startnode)
    return path


# In[ ]:


for issuekey,issue in tqdm(tags.iterrows(),total=tags.shape[0]):
    if issue['tagger'] in ptonum and issue['taggee'] in ptonum:
        taggernum = ptonum[issue['tagger']]
        taggeenum = ptonum[issue['taggee']]
        tagadj[taggeenum][taggernum] = tagadj[taggernum][taggeenum] = tagadj[taggernum][taggeenum]+1


# In[ ]:


tagadj = normalize(tagadj)


# ## prepare teamlist for next step

# In[ ]:


with open(filepathhelper.path(dataset,'train_team.json')) as json_file:
    data = json.load(json_file)
    issueteam = pd.DataFrame(data)


# In[ ]:


teamdict = {}
tempmapper = {'developer': 'dev',
 'integrator': 'integrator',
 'tester': 'tester',
 'reviewer': 'peer',
 'assignee': 'assignee'}
for key,issue in tqdm(issueteam.iterrows(),total=issueteam.shape[0]):
    issuekey = issue['issue']
    teamlist = issue['r'][0]['team']
    team = set()
    for t in teamlist:
        for p in teamlist[t]:
            if str(p)!='nan':
                num = ptonum[p]
                team.add((tempmapper[t],num))
    teamdict[issuekey]=team
    


# In[ ]:


chunkteamdict = {}
for i in tqdm(teamdict):
    issuekey = i.split('_')[1]
    if issuekey not in chunkteamdict:
        chunkteamdict[issuekey] = []
    chunkteamdict[issuekey].append(i)


# ## make csv for linear regression

# In[ ]:


def traincsvcal(chunkid):
    teamids = chunkteamdict[chunkid]
    temp = tempworkadj.copy()
    member = set()
    for role,num in teamdict[teamids[0]]:
        member.add(num)
    for i in member:
        for j in member:
            if i!=j:
                temp[i][j] = temp[j][i] = temp[j][i]-1
    temp[(temp!=0)&(temp!=math.inf)]=1
    temp = floyd_warshall(temp)
    chunkresults = []
    for t in teamids:
        re=0
        e=0
        we=0
        wr=0
        cl=0
        cn=0
        team = set()
        count = 0
        for role,num in teamdict[t]:
            team.add(num)
            if(role=='dev'):
                re = re + roleexp_dev[num]
                count=count+1
            if(role=='integrator'):
                re = re + roleexp_integrator[num]
                count=count+1
            if(role=='peer'):
                re = re + roleexp_peer[num]
                count=count+1
            if(role=='tester'):
                re = re + roleexp_test[num]
                count=count+1
            if(role=='assignee'):
                re = re + roleexp_assignee[num]  
                count=count+1
            e = e + experience[num]
            we = we + winexp[num]
            wr = wr + winrate[num]


        if len(team)>1:
            teamlis = list(team)
            for i in range(len(teamlis)):
                for j in range(i+1,len(teamlis)):
                    p1 = teamlis[i]
                    p2 = teamlis[j]
                    if temp[p1][p2]==math.inf:
    #                 if workadj[p1][p2]==math.inf:
                        cl = cl+1/len(allpp)
                    else:
                        cl = cl+1/temp[p1][p2]
    #                     cl = cl+1/workadj[p1][p2]

                    cn = cn+tagadj[p1][p2]
            cl = cl*2/len(teamlis)/(len(teamlis)-1)
            cn = cn*2/len(teamlis)/(len(teamlis)-1)
        winlist = winissues['issuekey'].tolist()
        chunkresults.append({'issuekey':t,'experience':e/count,'winexperience':we/count,'winrate':wr/count,'roleexperience':re/count,'closeness':cl,'connection':cn,'result':"Win" if t.startswith('real_') else "NotWin"})
    return chunkresults

with mp.Pool(NUMTHREAD) as p:
    multi_out = tqdm(p.imap(traincsvcal,chunkteamdict,chunksize=1),total=len(chunkteamdict))
    out = [i for i in multi_out]

csvforlin = []
for i in out:
    csvforlin.extend(i)
    
df = pd.DataFrame(csvforlin)


# In[ ]:


df[(df['result']=='Win')].describe()


# In[ ]:


df[(df['result']=='NotWin')].describe()


# In[ ]:


df.drop(columns=['issuekey'],inplace=True)


# In[ ]:


df.to_csv('baseline_feature_hitnohit_'+dataset+'.csv')


# In[ ]:


import pickle
with open(filepathhelper.path(dataset,'haibin/ptonum'),'wb') as f:
    pickle.dump(ptonum,f)
with open(filepathhelper.path(dataset,'haibin/roleexp_dev'),'wb') as f:
    pickle.dump(roleexp_dev,f)
with open(filepathhelper.path(dataset,'haibin/roleexp_integrator'),'wb') as f:
    pickle.dump(roleexp_integrator,f)
with open(filepathhelper.path(dataset,'haibin/roleexp_peer'),'wb') as f:
    pickle.dump(roleexp_peer,f)
with open(filepathhelper.path(dataset,'haibin/roleexp_test'),'wb') as f:
    pickle.dump(roleexp_test,f)
with open(filepathhelper.path(dataset,'haibin/roleexp_assignee'),'wb') as f:
    pickle.dump(roleexp_assignee,f)
with open(filepathhelper.path(dataset,'haibin/experience'),'wb') as f:
    pickle.dump(experience,f)
with open(filepathhelper.path(dataset,'haibin/winexp'),'wb') as f:
    pickle.dump(winexp,f)
with open(filepathhelper.path(dataset,'haibin/winrate'),'wb') as f:
    pickle.dump(winrate,f)
with open(filepathhelper.path(dataset,'haibin/workadj'),'wb') as f:
    pickle.dump(workadj,f)
with open(filepathhelper.path(dataset,'haibin/tagadj'),'wb') as f:
    pickle.dump(tagadj,f)
with open(filepathhelper.path(dataset,'haibin/weight'),'wb') as f:
    pickle.dump(weight,f)
with open(filepathhelper.path(dataset,"predecessors_workadj"),"wb") as f:
    pickle.dump(predes, f)

