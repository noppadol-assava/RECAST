#!/usr/bin/env python
# coding: utf-8

# In[ ]:

from featurev1 import *


# # Train

# In[3]:

with open(filepathhelper.path(dataset,'train_team.json')) as json_file:
    data = json.load(json_file)
#    issueteam = pd.DataFrame(data)
winissueset = set(winissues['issuekey'])
temp = {}
for i in tqdm(data):
#    temp[i['issue']]={'r':i['r'],'components':i['components'],'result': 'Win' if i['issue'].startswith('real') else 'NotWin'}
    temp[i['issue']]={'r':i['r'],'components':i['components'],'result': 'Win' if i['issue'] in winissueset else 'NotWin'}
issueteam = temp

# In[4]:

#issueteam['result'] =['Win' if i else 'NotWin' for i in issueteam['issue'].str.startswith('real')]
#issueteam['result'] =  ['Win' if i==True else 'NotWin' for i in issueteam['issue'].isin(winissues['issuekey'])]
#issueteam = issueteam[['issue','result']]

issuekeylist = list(issueteam.keys())


del data
import gc
gc.collect()

# In[ ]:


# IssueFamiliarity(issueteam.loc[20]['r'][0]['team'],issuekey=issueteam.loc[20]['issue'])
# SkillDiversity(issueteam.loc[20]['r'][0]['team'],issueteam.loc[20]['components'])
# SkillCompetency(issueteam.loc[20]['r'][0]['team'],issueteam.loc[20]['components'])
# team_interaction_score(issueteam.loc[2000]['r'][0]['team'])
# NumWorkTogether(issueteam.loc[2000]['r'][0]['team'])
# TeamRelateness(issueteam.loc[2000]['r'][0]['team'],1000)
# # IssueCloseness(issueteam.loc[2000]['r'][0]['team'],1000)


# In[ ]:


#len(PtoI[issueteam.loc[2000]['r'][0]['team']['tester'][0]])


# In[ ]:


#len(PtoI[issueteam.loc[2000]['r'][0]['team']['assignee'][0]])


# In[ ]:


#issueteam.head()


# In[ ]:


# ifam = []
# sd =[]
# sc =[]
# tisp = []
# tisn = []
# numwork=[]
# tr=[]
# ic = []
# atisp=[]
# atisn=[]
# taisp=[]
# taisn=[]
# ar=[]
# ce=[]
# for key,issue in tqdm(issueteam.iterrows(),total=issueteam.shape[0]):
#     team = issue['r'][0]['team']
# #    ifam.append(IssueFamiliarity(team,issuekey=issue['issue']))
#     sd.append(SkillDiversity(team,issue['components'],isTrain=True))
#     sc.append(SkillCompetency(team,issue['components'],isTrain=True))
#     tis = team_interaction_score(team)
#     tisp.append(tis['teamscorepos'])
#     tisn.append(tis['teamscoreneg'])
#     atis = assignee_team_interaction_score(team)
#     atisp.append(atis['teamscorepos'])
#     atisn.append(atis['teamscoreneg'])
#     tais = assignee_team_interaction_score(team)
#     taisp.append(tais['teamscorepos'])
#     taisn.append(tais['teamscoreneg'])
#     numwork.append(NumWorkTogether(team))
#     tr.append(TeamRelateness(team,1000,precal = True))
#     ar.append(AssigneeTeamRelateness(team,1000,precal = True))
#     ic.append(IssueCloseness(team,1000,precal = True,isTrain=True))
#     ce.append(ComponentExperience(team,issue['components'],isTrain=True))
    
# #issueteam['issuefamiliarity']=ifam
# issueteam['skilldiversity']=sd
# issueteam['skillcompetency']=sc
# issueteam['team_positiveinteration']=tisp
# issueteam['team_negativeinteration']=tisn
# issueteam['assignee_team_positiveinteration']=atisp
# issueteam['assignee_team_negativeinteration']=atisn
# issueteam['team_assignee_positiveinteration']=taisp
# issueteam['team_assignee_negativeinteration']=taisn
# issueteam['numwork'] = numwork
# issueteam['teamrelateness'] = tr
# issueteam['assignee_teamrelatedness'] = ar
# issueteam['issuecloseness'] = ic
# issueteam['componentexperience'] = ce
# issueteam.drop(columns=['components','context','r'],inplace = True)
# issueteam.to_csv('features.csv')

def calculatefeature(issuekey):
    result = {}
    result['issuekey']=issuekey
##    issue = issueteam.loc[issuekey]
    issue = issueteam[issuekey]
##
    team = issue['r'][0]['team']
    if '_' in issuekey:
        issuekey = issuekey.split('_')[1]
#    ifam.append(IssueFamiliarity(team,issuekey=issue['issue']))
    result['issuefamiliarity'] = IssueFamiliarity(team,issuekey=issuekey)
    result['skilldiversity']=SkillDiversity(team,issue['components'],isTrain=True)
    result['skillcompetency']=SkillCompetency(team,issue['components'],isTrain=True)
    tis = team_interaction_score(team)
    result['team_positiveinteration']= tis['teamscorepos']
    result['team_negativeinteration'] = tis['teamscoreneg']
    
    atis = assignee_team_interaction_score(team)
    result['assignee_team_positiveinteration']=atis['teamscorepos']
    result['assignee_team_negativeinteration']=atis['teamscoreneg']
    
    tais = assignee_team_interaction_score(team)
    result['team_assignee_positiveinteration']=tais['teamscorepos']
    result['team_assignee_negativeinteration']=tais['teamscoreneg']
    
    result['numwork'] = NumWorkTogether(team)
    result['teamrelateness'] = TeamRelateness(team,1000,precal = True)
    result['assignee_teamrelatedness'] = AssigneeTeamRelateness(team,1000,precal = True)
    result['issuecloseness'] = IssueCloseness(team,1000,precal = True,isTrain=True)
    result['componentexperience'] = ComponentExperience(team,issue['components'],isTrain=True)
    result['projectexperience'] = ProjectExperience(team,proj = re.match(r"(.*?)-", issuekey).group(1),isTrain=True)
    result['groupcontribution'] = getGroupContribution(team)
    result['result'] = issue['result']
    return result

NUMTHREAD = 5
#issuekeylist = list(issueteam['issue'])
#issueteam.set_index('issue',inplace=True)
with mp.Pool(NUMTHREAD) as p:
    multi_out = tqdm(p.imap(calculatefeature,issuekeylist,chunksize=1),total=len(issuekeylist))
    result = [i for i in multi_out]
    
output = pd.DataFrame(result)
output.to_csv('features_atlassian.csv')

import requests

url = 'https://notify-api.line.me/api/notify'
token = 'ZYudxqEudSPHqJ3WqFT2HJGgQauUOhHQV2LMDEmlXTm'
headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}

msg = 'Feature Calculation เสร็จแล้ว'
r = requests.post(url, headers=headers , data = {'message':msg})
print (r.text)

# In[ ]:


# os.system("shutdown /s /t 1");


# In[ ]:


# IssueFamiliarity(issueteam.loc[20]['r'][0]['team'],issuekey=issueteam.loc[20]['issue'])
# SkillDiversity(issueteam.loc[20]['r'][0]['team'],issueteam.loc[20]['components'])
# SkillCompetency(issueteam.loc[20]['r'][0]['team'],issueteam.loc[20]['components'])
# team_interaction_score(issueteam.loc[2000]['r'][0]['team'])
# NumWorkTogether(issueteam.loc[2000]['r'][0]['team'])
# TeamRelateness(issueteam.loc[2000]['r'][0]['team'],1000)
# # IssueCloseness(issueteam.loc[2000]['r'][0]['team'],1000)


# In[5]:


# ITER = 100
# import timeit


# In[6]:


# ar = np.array([])
# for i in tqdm(range(0,ITER)):
#     start = timeit.default_timer()
#     IssueFamiliarity(issueteam.loc[i]['r'][0]['team'],issuekey=issueteam.loc[i]['issue'])
#     stop = timeit.default_timer()
#     ar = np.append(ar,stop-start)
# ar.mean()


# In[7]:


# ar = np.array([])
# for i in tqdm(range(0,ITER)):
#     start = timeit.default_timer()
#     TeamRelateness(issueteam.loc[i]['r'][0]['team'],1000)
#     stop = timeit.default_timer()
#     ar = np.append(ar,stop-start)
# ar.mean()


# In[8]:


# ar = np.array([])
# for i in tqdm(range(0,ITER)):
#     start = timeit.default_timer()
#     SkillDiversity(issueteam.loc[i]['r'][0]['team'],issueteam.loc[i]['components'])
#     SkillCompetency(issueteam.loc[i]['r'][0]['team'],issueteam.loc[i]['components'])
#     NumWorkTogether(issueteam.loc[i]['r'][0]['team'])
#     stop = timeit.default_timer()
#     ar = np.append(ar,stop-start)
# ar.mean()


# In[9]:


# ar = np.array([])
# for i in tqdm(range(0,ITER)):
#     start = timeit.default_timer()
#     team_interaction_score(issueteam.loc[i]['r'][0]['team'])
#     stop = timeit.default_timer()
#     ar = np.append(ar,stop-start)
# ar.mean()


# In[ ]:




