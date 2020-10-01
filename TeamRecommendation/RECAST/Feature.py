
#!/usr/bin/env python
# coding: utf-8

# In[1]:

# NUMTHREADS = 20


# In[2]:


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


# In[1]:


import math
import random
import pandas as pd
import numpy as np
import cupy as cp
from tqdm import tqdm
import pickle
# from tqdm import tqdm_notebook as tqdm
import subprocess
import ast
from neo4j import GraphDatabase
import neo4j
import multiprocessing as mp
from functools import lru_cache
import hashlib
import re
from networkx.algorithms.approximation import steiner_tree
# # File Need

# In[4]:


teams = pd.read_csv(filepathhelper.path(dataset,'team.csv'))
closeresolve = pd.read_csv(filepathhelper.path(dataset,'closeresolve.csv'),sep=';')
winissues = pd.read_csv(filepathhelper.path(dataset,'winissue.csv'))
assignees = pd.read_csv(filepathhelper.path(dataset,'assignee.csv'),sep=';')
trainset = pd.read_csv(filepathhelper.path(dataset,'trainissuekey.csv'))
issuecomponent = pd.read_csv(filepathhelper.path(dataset,'component_title.csv'),sep=';;;',engine='python')
#######################################################################################
df = pd.read_csv(filepathhelper.path(dataset,'global_pair_score.csv') , encoding='iso-8859-1')

pos = df['positivescore']
neg = df['negativescore']
    
    #normalize values
posnorm=(pos-pos.min())/(pos.max()-pos.min())
negnorm = (neg - neg.min())/(neg.max()-neg.min())
    
df['positivescore'] = posnorm
df['negativescore'] = negnorm
    
df.set_index(['tagger', 'taggee'])
#######################################################################################

# In[5]:


teams = teams[(teams['issuekey'].isin(closeresolve['issuekey']))]
assignees = assignees[(assignees['issuekey'].isin(teams['issuekey']))]
teams = teams[teams['issuekey'].isin(trainset['issuekey'])]
assignees = assignees[assignees['issuekey'].isin(trainset['issuekey'])]
winissues = winissues[winissues['issuekey'].isin(trainset['issuekey'])]


# # Initialize Variable

# In[6]:


with open(filepathhelper.path(dataset,'topdistdf'),'rb') as f:
    topdists = pickle.load(f)
topdists.set_index('issuekey',inplace=True)


# In[7]:


with open(filepathhelper.path(dataset,'PtoI'),'rb') as f:
    PtoI = pickle.load(f)


# In[8]:


with open(filepathhelper.path(dataset,'worktogether'),'rb') as f:
    worktogether = pickle.load(f)


# In[9]:


with open(filepathhelper.path(dataset,'ItoC'),'rb') as f:
    ItoC = pickle.load(f)


# In[10]:


with open(filepathhelper.path(dataset,'rp'),'rb') as f:
    rp = pickle.load(f)
    
with open(filepathhelper.path(dataset,'PPsp'),'rb') as f:
    PPsp = pickle.load(f)
    
with open(filepathhelper.path(dataset,'IIsp'),'rb') as f:
    IIsp = pickle.load(f)

with open(filepathhelper.path(dataset,'ProjExp'),'rb') as f:
    ProjExp = pickle.load(f)

# In[11]:


PtoC = {}
for p in PtoI:
    if p not in PtoC:
        PtoC[p] = {}
    issues = PtoI[p]
    for issue in issues:
        if issue in ItoC:
            for component in ItoC[issue]:
                if component not in PtoC[p]:
                    PtoC[p][component]=0
                PtoC[p][component]=PtoC[p][component]+1


# In[2]:


# url = "bolt://localhost:7687"
# driver = GraphDatabase.driver(url, auth=("neo4j", "jrdb"))
# url = "bolt://10.34.2.140:7687"
# driver = GraphDatabase.driver(url, auth=("neo4j", "jrdb"))


# # Feature

# ## Issue Familiarity

# In[32]:


def IssueFamiliarity(team,issuekey='',descript='',fortest=False):
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = set(member)
    if descript != '':
        with open("temp.txt", "w") as f:
            f.write(descript)
        subprocess.call(['java', '-jar', 'topicSim.jar',filepathhelper.path(dataset,'model_nonLabel_500_9_1'),'temp.txt'])
        with open("topicDist", "r") as f:
            s = f.read().split('\n')[:-1]
        tdin = ast.literal_eval(s[0])

        os.remove("temp.txt")
        os.remove("topicDist")
    elif issuekey != '' and not fortest:
        inissuerow = topdists.loc[issuekey]
        tdin = inissuerow['topdist'] #faster
        tdin_squaresum = inissuerow['squaresum'] #faster
        tdin = cp.array(tdin) #gpu
        tdin_squaresum = cp.array(tdin_squaresum) #gpu
        #tdin_squaresum = math.sqrt((np.array(tdin)**2).sum()) #faster
        
    issuefam = 0
    if fortest:
        issuefam = np.array([maxcosim(m,issuekey) for m in member]).sum()
    else:
        for m in member:
            if m not in PtoI:
                continue
            participated_issue = PtoI[m].copy()
            participated_issue.discard(issuekey)
            if len(participated_issue)>0:   
                participated_issue_topdist = topdists.loc[participated_issue]
                todistmatrix = cp.array([cp.array(i) for i in participated_issue_topdist['topdist'].values])
                squaresum = cp.array(participated_issue_topdist['squaresum'].values)
                maxfam = (todistmatrix.dot(tdin)/(squaresum*tdin_squaresum)).max()

    #             num_participated  = participated_issue_topdist.shape[0]
    #             pitd_squaresum = participated_issue_topdist['squaresum']
    #             pitd = participated_issue_topdist['topdist']
    #             tdin_squaresum_list = [tdin_squaresum for i in range(0,num_participated)]
    #             tdin_list = [tdin for i in range(0,num_participated)]
    #             cosinargs = tuple(zip(pitd_squaresum,pitd,tdin_squaresum_list,tdin_list))  

    #             with mp.Pool(NUMTHREADS) as pool:
    #                 result = pool.starmap(cosim,cosinargs, chunksize=NUMTHREADS)
    #                 maxfam = np.array([i for i in result]).max()
    #             for issue in participated_issue:
    #                 issuerow = topdists.loc[issue]
    #                 td = issuerow['topdist']
    #                 td_squaresum = issuerow['squaresum']
    #                 maxfam = max(maxfam,cosim(td_squaresum,td,tdin_squaresum,tdin))
                issuefam = issuefam+maxfam
    return float(issuefam)/len(member)

@lru_cache(100000)
def maxcosim(username,issuekeyin):
    inissuerow = topdists.loc[issuekeyin]
    tdin = inissuerow['topdist'] #faster
    tdin_squaresum = inissuerow['squaresum'] #faster
    
    tdin = cp.array(tdin) #gpu
    tdin_squaresum = cp.array(tdin_squaresum) #gpu
    
    participated_issue = [] if str(username)=='nan' or username not in PtoI else PtoI[username].copy()
    maxfam =0
    if len(participated_issue)>0:   
        participated_issue_topdist = topdists.loc[participated_issue]
        todistmatrix = cp.array([cp.array(i) for i in participated_issue_topdist['topdist'].values])
        squaresum = cp.array(participated_issue_topdist['squaresum'].values)
        maxfam = (todistmatrix.dot(tdin)/(squaresum*tdin_squaresum)).max()
    return maxfam

def cosim(td1_squaresum,td1,td2_squaresum,td2):
#     dot = 0
#     for i in range(0,len(td2)):
#         dot=dot+td1[i]*td2[i]
    return np.array(td1).dot(np.array(td2))/(td1_squaresum*td2_squaresum)


# ## Team Issue Relateness

# In[33]:


def shortestpath_issue(tx,issue1,issue2):
    if issue1==issue2:
        return 0
    result = tx.run("MATCH (start:Issue{name:$issue1}), (end:Issue{name:$issue2}) "
            "CALL algo.shortestPath.stream(start, end, 'weight') "
            "YIELD nodeId, cost "
            "RETURN algo.asNode(nodeId).name AS name, cost",issue1=issue1,issue2=issue2)
    temp = neo4j.Record(iter(result))
    return temp[len(temp)-1] if len(temp)>0 else math.inf

@lru_cache(100000)
def shortestpath(typ,obj1,obj2):
    #print(obj1,' ',obj2)
    if typ =='issue':
        func = shortestpath_issue
    elif typ =='person':
        func = shortestpath_person
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "jrdb"))
    with driver.session() as session:
        sp = session.read_transaction(func, obj1, obj2)
    driver.close()
    return sp
    
def IssueRelateness(team,related_issue,MAXLENGTH):
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = set(member)
    
    sumsp = 0
    for m in member:
        if m not in PtoI:
            continue
        participated_issue = PtoI[m]
        minsp = math.inf
        for hisissue in related_issue:
            for issue in participated_issue:
                if minsp ==0:
                    break;
                minsp = min(minsp,shortestpath('issue',hisissue,issue))
        minsp = minsp +1
        minsp = min(minsp,MAXLENGTH)
#         if minsp > MAXLENGTH:
#             minsp = MAXLENGTH
        sumsp = sumsp+minsp
    return len(member)/sumsp
    
# with driver.session() as session:
#     sp = session.read_transaction(shortestpath, 'pilpi', 'cibot')
#     print(sp)


# ## Team Issue Closeness

# In[34]:

ICcache = {}

def IssueCloseness(team,MAXLENGTH,precal =False,isTrain=False):
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = set(member)

    sumsp = 0
    if 1>0:
#     for m in member:
        m = team['assignee'][0]
        for n in member:
            if m!=n and m in PtoI and n in PtoI:
                
                hashmn = hashlib.sha1(str((m,n)).encode()).hexdigest()
                hashnm = hashlib.sha1(str((m,n)).encode()).hexdigest()
                if hashmn in ICcache:
                    minsp = ICcache[hashmn]
                elif hash((n,m)) in ICcache:
                    minsp = ICcache[hashnm]
                else:
                    minsp = math.inf
                    for missue in PtoI[m]:
                        for nissue in PtoI[n]:
                            if missue == nissue and isTrain:
                                continue
                            if precal:
                                sp = IIsp[missue][nissue] if missue in IIsp and nissue in IIsp[missue] else math.inf
                            else:
                                sp = shortestpath('issue',missue,nissue)
                            minsp = min(minsp,sp)
                    minsp = min(minsp,MAXLENGTH)
                ICcache[hashmn]=minsp
                sumsp = sumsp+minsp
    sumsp = sumsp +1 #smoothing
    return len(member)*(len(member)-1)/sumsp
    


# ## Co-worker

# In[35]:


def shortestpath_person(tx,person1,person2):
    if person1==person2:
        return 0
    result = tx.run("MATCH (start:Person{name:$person1}), (end:Person{name:$person2}) "
            "CALL algo.shortestPath.stream(start, end, 'weight') "
            "YIELD nodeId, cost "
            "RETURN algo.asNode(nodeId).name AS name, cost",person1=person1,person2=person2)
    temp = neo4j.Record(iter(result))
    return temp[len(temp)-1] if len(temp)>0 else math.inf

TRcache = {}

def TeamRelateness(team,MAXLENGTH,precal = False):
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = set(member)
    sumsp = 0
    for m in member:
        for n in member:
            if m!=n:
                hashmn = hashlib.sha1(str((m,n)).encode()).hexdigest()
                hashnm = hashlib.sha1(str((n,m)).encode()).hexdigest()
                if hashmn in TRcache:
                    sp = TRcache[hashmn]
                elif hash((n,m)) in TRcache:
                    sp = TRcache[hashnm]
                else:
                    if precal:
                        try:
                            sp = PPsp[m][n] if m in PPsp and n in PPsp else math.inf
                        except:
                            sp = math.inf
                    else:
                        sp = shortestpath('person',m,n)
                sp = min(sp,MAXLENGTH)
                TRcache[hashmn]=sp
#                 if sp > MAXLENGTH:
#                     sp = MAXLENGTH
                sumsp = sumsp+sp 
                
    sumsp = sumsp+1  #smoothing
    return len(member)*(len(member)-1)/sumsp

def AssigneeTeamRelateness(team,MAXLENGTH,precal = False):
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']
    member = set(member)
    sumsp = 0
#     for m in member:
    if 1>0:
        m = team['assignee'][0]
        for n in member:
            if m!=n:
                hashmn = hashlib.sha1(str((m,n)).encode()).hexdigest()
                hashnm = hashlib.sha1(str((n,m)).encode()).hexdigest()
                if hashmn in TRcache:
                    sp = TRcache[hashmn]
                elif hash((n,m)) in TRcache:
                    sp = TRcache[hashnm]
                else:
                    if precal:
                        try:
                            sp = PPsp[m][n] if m in PPsp and n in PPsp else math.inf
                        except:
                            sp = math.inf
                    else:
                        sp = shortestpath('person',m,n)
                sp = min(sp,MAXLENGTH)
                TRcache[hashmn]=sp
#                 if sp > MAXLENGTH:
#                     sp = MAXLENGTH
                sumsp = sumsp+sp 
                
    sumsp = sumsp+1  #smoothing
    return (len(member.union(set([team['assignee'][0]])))-1)/sumsp 
                
                


# In[36]:


def NumWorkTogether(team):
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = set(member)
    numworktogether = 0
    for m in member:
        for n in member:
            if m!=n:
                numworktogether = numworktogether+worktogether[m][n]
    return numworktogether/(len(member)*(len(member)-1)) if len(member)>1 else 0


# ## Skill Diversity

# In[37]:


def SkillDiversity(team,reqskill,isTrain=False):
    reqskill = set(reqskill)
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = set(member)
    numskill = 0
    uniqueskill = set()
    for m in member:
        skill = set()
        if m in PtoC:
            for c in PtoC[m]:
                numcomp = PtoC[m][c]-1 if isTrain else PtoC[m][c]
                if numcomp>0:
                    skill.add(c)
        uniqueskill.update(skill)
        numskill = numskill+len(skill)
    numskill = numskill+1
    return len(uniqueskill)/numskill


# ## Skill Competenct/Satisfaction

# In[38]:


def SkillCompetency(team,reqskill,isTrain=False):
    reqskill = set(reqskill)
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = set(member)
    uniqueskill = set()
    for m in member:
        skill = set()
        if m in PtoC:
            for c in PtoC[m]:
                numcomp = PtoC[m][c]-1 if isTrain else PtoC[m][c]
                if numcomp>0 and c in reqskill:
                    skill.add(c)
        uniqueskill.update(skill)
    return len(uniqueskill)/(len(reqskill)+1)


# ## Interaction Score

# In[39]:

@lru_cache(100000)
def pair_score(tagger, taggee):
    
    s = df.loc[(df['tagger'] == tagger) & (df['taggee'] == taggee), ['tagger','taggee','positivescore', 'negativescore']]
    if len(s['tagger'].values) != 0:
        score = {'posscore': s['positivescore'].values[0], 'negscore': s['negativescore'].values[0]}
    else:
        score = {'posscore': 0, 'negscore': 0}
    return score

def team_interaction_score(team):
    
    #pair every member in team
    member = set(team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee'])
#    member = pd.Series(member).drop_duplicates().tolist()
    teamscorepos = 0
    teamscoreneg = 0
    pscoremat = []  
    nscoremat = [] 
    if len(member) > 1:        
        for m in member:
            ps = []
            ns = []
            for n in member:
                if m != n:
                    score = pair_score(m,n)
                    ps.append(score['posscore'])
                    ns.append(score['negscore'])
                else:
                    ps.append(0)
                    ns.append(0)
            pscoremat.append(ps)
            nscoremat.append(ns)        
        numCombination = len(member)*(len(member)-1)
        
        return {'teamscorepos':float(np.array(pscoremat).sum())/numCombination ,'teamscoreneg':float(np.array(nscoremat).sum())/numCombination }  
    return {'teamscorepos':0,'teamscoreneg':0}

def team_interaction_change(previousTeam, previousScore, currentTeam):
    
    previousmember = previousTeam['developer'] + previousTeam['integrator']+ previousTeam['tester'] + previousTeam['reviewer']+previousTeam['assignee']
    currentmember = currentTeam['developer'] + currentTeam['integrator']+ currentTeam['tester'] + currentTeam['reviewer']+currentTeam['assignee']
    
    #preserve order
    previousmember = pd.Series(previousmember).drop_duplicates().tolist()
    currentmember = pd.Series(currentmember).drop_duplicates().tolist()
    
    #inmember = set(currentmember) -set(previousmember)
    inmember = [i for i in currentmember if i not in previousmember]
    #outmember = set(previousmember)-set(currentmember)
    outmember = [i for i in previousmember if i not in currentmember]
    
#     print('Change out: ', outmember,  '  Change in: ', inmember)
#     print('Current combination: ', len(currentmember)*(len(currentmember)-1))
    
    if len(previousScore) == 0 or len(previousmember) == 0:
#         Find normal score if there is no previus team
        return team_interaction_score(currentTeam)
    else:
        pos = previousScore['teamscorepos']
        neg = previousScore['teamscoreneg']
        
        for i in outmember:
            index = previousmember.index(i)
            pos = np.delete(pos, index, axis=1)
            neg = np.delete(neg, index, axis=1)
            
            pos = np.delete(pos, index, axis=0)
            neg = np.delete(neg, index, axis=0)
            previousmember.remove(i)
            
        pos = pos.tolist()
        neg = neg.tolist()
        
        for i in inmember:
            ps = []
            ns = []
            for j in previousmember:
                score = pair_score(i,j)
                ps.append(score['posscore'])
                ns.append(score['negscore'])
#                 print('add: ',i,'-->',j, score['posscore'],'  ',score['negscore'])
            pos.append(ps)
            neg.append(ns)
                
                
        for i in inmember:
            for j in previousmember:
                score = pair_score(j,i)
                pos[previousmember.index(j)].append(score['posscore'])
                neg[previousmember.index(j)].append(score['negscore'])
#                 print('add: ',j,'-->',i, score['posscore'],'  ',score['negscore'])
        
        #print(pos, neg)
        return {'teamscorepos':pos,'teamscoreneg':neg}

def assignee_team_interaction_score(team):
    
    #pair every member in team
    member = set(team['developer'] + team['integrator']+ team['tester'] + team['reviewer'])
#    member = pd.Series(member).drop_duplicates().tolist()
    teamscorepos = 0
    teamscoreneg = 0
    pscoremat = []  
    nscoremat = [] 
    if len(member.union(set([team['assignee'][0]])))-1>0:        
#         for m in member:
        if 1>0:
            m = team['assignee'][0]
            ps = []
            ns = []
            for n in member:
                if m != n:
                    score = pair_score(m,n)
                    ps.append(score['posscore'])
                    ns.append(score['negscore'])
                else:
                    ps.append(0)
                    ns.append(0)
            pscoremat.append(ps)
            nscoremat.append(ns)        
        numCombination = len(member.union(set([team['assignee'][0]])))-1
        
        return {'teamscorepos':np.array(pscoremat).sum()/numCombination ,'teamscoreneg':np.array(nscoremat).sum()/numCombination }  
    return {'teamscorepos':0,'teamscoreneg':0}

def team_assignee_interaction_score(team):
    #pair every member in team
    member = set(team['developer'] + team['integrator']+ team['tester'] + team['reviewer'])
#    member = pd.Series(member).drop_duplicates().tolist()
    teamscorepos = 0
    teamscoreneg = 0
    pscoremat = []  
    nscoremat = [] 
    if len(member.union(set([team['assignee'][0]])))-1 > 0:        
        for m in member:
            ps = []
            ns = []
#             for n in member:
            if 1>0:
                n = team['assignee'][0]
                if m != n:
                    score = pair_score(m,n)
                    ps.append(score['posscore'])
                    ns.append(score['negscore'])
                else:
                    ps.append(0)
                    ns.append(0)
            pscoremat.append(ps)
            nscoremat.append(ns)        
        numCombination = len(member.union(set([team['assignee'][0]])))-1
        
        return {'teamscorepos':np.array(pscoremat).sum()/numCombination ,'teamscoreneg':np.array(nscoremat).sum()/numCombination }  
    return {'teamscorepos':0,'teamscoreneg':0}

def ComponentExperience(team,reqskill,isTrain=False):
    reqskill = set(reqskill)
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = set(member)
    totalexp = 0
    for m in member:
        if m in PtoC:
            for c in PtoC[m]:
                numcomp = PtoC[m][c]-1 if isTrain else PtoC[m][c]
                if c in reqskill:
                    totalexp = totalexp+numcomp
    return totalexp/((len(reqskill)+1)*len(member))

def ProjectExperience(team,proj,isTrain=False):
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = set(member)
    totalexp = 0
    for m in member:
        if m in ProjExp and proj in ProjExp[m]:
            totalexp = totalexp + (ProjExp[m][proj] - 1 if isTrain else ProjExp[m][proj])
    return totalexp/len(member)
    
contribution = pd.read_csv(filepathhelper.path(dataset,r'contribution.csv'))
contributor = set(contribution['username'])
contribution.set_index('username',inplace=True)

def getGroupContribution(team):
    t = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    t = set(t)
    return contribution.loc[contributor.intersection(t)]['contribution'].sum()/len(t)
#    t = list(set(t))
#    score = []
#    for i in t:
#        if i in contributor:
#            score.append(contribution.loc[i]['contribution'])
#        else:
#            score.append(0)
#    return sum(score)/len(score)

########################################################### Haibin Feature #######################################################
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



    
def haibinfeaturecalculation(team):
    countrole = len(team['developer'])+len(team['integrator'])+len(team['tester'])+len(team['reviewer'])+len(team['assignee'])
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = [ptonum[i] for i in set(member)]
    e=0
    we=0
    wr=0
    re=0
    cl=0
    cn=0
    for i in team['developer']:
        num = ptonum[i]
        re = re+roleexp_dev[num]
        e = e + experience[num]
        we = we + winexp[num]
        wr = wr + winrate[num]
    for i in team['integrator']:
        num = ptonum[i]
        re = re+roleexp_integrator[num]
        e = e + experience[num]
        we = we + winexp[num]
        wr = wr + winrate[num]
    for i in team['reviewer']:
        num = ptonum[i]
        re = re+roleexp_peer[num]
        e = e + experience[num]
        we = we + winexp[num]
        wr = wr + winrate[num]
    for i in team['tester']:
        num = ptonum[i]
        re = re+roleexp_test[num]
        e = e + experience[num]
        we = we + winexp[num]
        wr = wr + winrate[num]
    for i in team['assignee']:
        num = ptonum[i]
        re = re+roleexp_assignee[num]
        e = e + experience[num]
        we = we + winexp[num]
        wr = wr + winrate[num]
    re = re/countrole
    e = e/countrole
    we = we/countrole
    wr = wr/countrole
    if len(member)>1:
        for i in range(len(member)):
            for j in range(i+1,len(member)):
                p1 = member[i]
                p2 = member[j]
                if workadj[p1][p2]==math.inf:
                    cl = cl+1/len(ptonum)
                else:
                    cl = cl+1/workadj[p1][p2]
                cn = cn+tagadj[p1][p2]
        cl = cl*2/len(member)/(len(member)-1)
        cn = cn*2/len(member)/(len(member)-1)
    return {'experience':e,'winexperience':we,'winrate':wr,'roleexperience':re,'closeness':cl,'connection':cn}


########################### EVAL Matrices ###########################
def CCR(team):
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = [ptonum[i] for i in set(member)]
    dia = 0
    if len(member)>1:
        for i in range(len(member)):
            for j in range(i+1,len(member)):
                m=member[i]
                n=member[j]
                sp = workadj[m][n] 
                dia = max(dia,sp)
    return dia


with open(filepathhelper.path(dataset,'predecessors_workadj'),'rb') as f:
    predecessors_workadj=pickle.load(f)
    
def pathtracking(predecessors,startnode,endnode):
    path = []
    i = endnode
    while i != startnode and i!=-9999:
        path.append(i)
        i = predecessors[startnode, i]
    path.append(startnode)
    return path

def CCSteiner(team):
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = [ptonum[i] for i in set(member)]
    cc = 0
    x = random.choice(member)
    member.remove(x)
    treenode = set([x])
    while len(member) != 0:
        startnode=-1
        endnode=-1
        sp = math.inf
        for m in member:
            for n in treenode:
                spij =workadj[m][n]
                if spij<sp:
                    sp = spij
                    startnode=m
                    endnode=n
        if sp != math.inf:
            member.remove(startnode)
            cc=cc+sp
            treenode.update(pathtracking(predecessors_workadj,startnode,endnode))
        else:
            return math.inf
    return cc

def CCSD(team):
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']+team['assignee']
    member = [ptonum[i] for i in set(member)]
    cc=0
    if len(member)>1:
        for i in range(len(member)):
            for j in range(i+1,len(member)):
                m=member[i]
                n=member[j]
                sp = workadj[m][n]
                cc = cc+sp
    return cc

def CCLD(team):
    leader = ptonum[team['assignee'][0]]
    member = team['developer'] + team['integrator']+ team['tester'] + team['reviewer']
    member = [ptonum[i] for i in set(member)]
    cc=0
    if len(member)>0:
        m=leader
        for n in member:
            sp = workadj[m][n]
            cc = cc+sp
    return cc
    
                
