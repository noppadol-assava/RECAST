
#!/usr/bin/env python
# coding: utf-8

# In[1]:

from Feature import *
import hashlib
import datetime as dt

# # Test

# In[ ]:


def hash_team(team):
    t_sorted = {i:sorted(team[i]) if type(team[i]) == list else team[i] for i in team}
    ## hash team
    t_hash = hashlib.sha1(json.dumps(t_sorted, sort_keys=True).encode()).hexdigest()
    return t_hash

allteam_cache = {}
def maxlogit(N,roles_pp,alpha,cost,context='',component='',issuekey=''):
    allteam_hash = set()
    allteam = []#tor add
    if individual:
        roles = [missingrole]
    else:
        roles = [r for r in roles_pp] 
        roles.remove('assignee') # not random assignee
    
    T = {roles_pp[0]:random.choice(roles_pp[1]) for roles_pp in roles_pp.items()} #1
    bestT=T #1
    if issuekey!='':
        cb = cost(bestT,context,component,issuekey=issuekey)
    else:
        cb = cost(bestT,context,component)
        
    allteam.append((bestT,cb[0],cb[1])) # tor add
    allteam_cache[hash_team(bestT)] = cb # tor add

    for i in range(1,N): #2
#     if N > 0:
        hashT = hash_team(T) #tor add
        if issuekey!='':
            c = cost(T,context,component,issuekey=issuekey) if hashT not in allteam_cache else allteam_cache[hashT] #3 tor modified
        else:
            c = cost(T,context,component) if hashT not in allteam_cache else allteam_cache[hashT] #3 tor modified
                
        Tp = T.copy() #4
        randomrole = random.choice(roles) #4 modified by tor (not change assignee)
        Tp[randomrole] = random.choice(roles_pp[randomrole]) #4
        
        # tor modified if team has been calculated before don't re calculate
        hashTP = hash_team(Tp)
                
        if issuekey!='':
            cp = cost(Tp,context,component,issuekey=issuekey) if hashTP not in allteam_cache else allteam_cache[hashTP] #5 tor modified
        else:
            cp = cost(Tp,context,component) if hashTP not in allteam_cache else allteam_cache[hashTP] #5 tor modified
            
        allteam.append((Tp,cp[0],cp[1])) # tor add
        allteam_cache[hashTP] = cp #tor add
        
        prob = probability(c[0],cp[0],alpha) #6
        r = random.uniform(0, 1) #7
        if r <= prob:#8
            T = Tp #9
            c = cp #9
#             allteam.append((T,c)) # tor add
            if c[0] < cb[0]: #10
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
    for t,s,f in team:
        t_sorted = {i:sorted(t[i]) if type(t[i]) == list else t[i] for i in t}
        ## hash team
        t_hash = hashlib.sha1(json.dumps(t_sorted, sort_keys=True).encode()).hexdigest()
        if t_hash not in hashteam:
            hashteam.add(t_hash)
            temp.append((t,s,f))
    team = temp
    team = team[:min(len(team),rank)]
    rank = []
    rankno=1
    team.sort(key=lambda tup: tup[1]) 
    for team,score,feature in team:
        rankdict = {'rank':rankno,'team':{'developer':[],'integrator':[],'tester':[],'reviewer':[],'assignee':[]},'cost':score,'features':feature}
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
        print('save successful')
def formatTeam(team):
    output_team = {'developer':[],'integrator':[],'tester':[],'reviewer':[],'assignee':[]}
    for r in team:
        if r =='assignee':
            output_team['assignee'].append(team[r])
        elif r.startswith('dev'):
            output_team['developer'].append(team[r])
        elif r.startswith('integrator'):
            output_team['integrator'].append(team[r])
        elif r.startswith('peer'):
            output_team['reviewer'].append(team[r])
        elif r.startswith('tester'):
            output_team['tester'].append(team[r])
    return output_team


# In[ ]:

with open(filepathhelper.path(dataset,'RandomForest.model'),'rb') as f:
    rfmodel = pickle.load(f)
rfmodel.set_params(n_jobs=None)
with open(filepathhelper.path(dataset,'normalize.dict'),'rb') as f:
    normalizedfeature = pickle.load(f)
    
def teamStrengthCost(Team,context,component,issuekey=''):
    team = formatTeam(Team)
    features = {}
    features.update(haibinfeaturecalculation(team))
    features['skilldiversity']=SkillDiversity(team,component,isTrain=False)
    features['skillcompetency']=SkillCompetency(team,component,isTrain=False)
    tis = team_interaction_score(team)
    features['team_positiveinteration']= tis['teamscorepos']
    features['team_negativeinteration'] = tis['teamscoreneg']
    
    atis = assignee_team_interaction_score(team)
    features['assignee_team_positiveinteration']=atis['teamscorepos']
    features['assignee_team_negativeinteration']=atis['teamscoreneg']
    
    tais = assignee_team_interaction_score(team)
    features['team_assignee_positiveinteration']=tais['teamscorepos']
    features['team_assignee_negativeinteration']=tais['teamscoreneg']
    
    features['numwork'] = NumWorkTogether(team)
    features['teamrelateness'] = TeamRelateness(team,1000,precal = True)
    features['assignee_teamrelatedness'] = AssigneeTeamRelateness(team,1000,precal = True)
    features['issuecloseness'] = IssueCloseness(team,1000,precal = True,isTrain=False)
    features['componentexperience'] = ComponentExperience(team,component,isTrain=False)
    features['issuefamiliarity'] = IssueFamiliarity(team,issuekey,fortest=True) if issuekey!='' else IssueFamiliarity(team,context)
    features['projectexperience'] = ProjectExperience(team,proj = re.match(r"(.*?)-", issuekey).group(1),isTrain=False)
    features['groupcontribution'] = getGroupContribution(team)
    features['CCR'] = CCR(team)
    features['CCSteiner'] = CCSteiner(team)
    features['CCSD'] = CCSD(team)
    features['CCLD'] = CCLD(team)
    #normalize
    for f in normalizedfeature:
        features[f] = (features[f] - normalizedfeature[f]['min'])/(normalizedfeature[f]['max']-normalizedfeature[f]['min'])
    inp_features = pd.DataFrame([features])[rfmodel.feature_names]
    prob = rfmodel.predict_proba(inp_features)[0][1]
    return (1/prob,features) if prob>0 else (math.inf,features)
#     return 1
# In[ ]:

useract = pickle.load( open( filepathhelper.path(dataset,"useractivity.p"), "rb" ) )
issueinfo = pd.read_csv(filepathhelper.path(dataset,'issueinformation.csv'),sep=';')
issueinfo = issueinfo[["issuekey","createdate"]]
issueinfo.set_index('issuekey',inplace=True)

@lru_cache(100000)
def isUserActive(username, opendate, excludekey, period, freq):
    active = False
    count = 0
    if username not in useract:
        return False
    activity = useract[username]
   
#     activity = activity.sort_values(['time'])

    starttime = opendate - dt.timedelta(days=period)
    for issue, time in activity:
        if issue != excludekey:
            if time < opendate and time > starttime:
                count = count +1
    if count > freq:
        active = True
    return active


filterstr = ''
period = 360
freq = 1
filter = sys.argv[1] == "True"

if filter:
    period = int(sys.argv[2])
    freq = int(sys.argv[3])
if filter:
    print('days: '+str(period))
    print('freq: '+str(freq))
    filterstr = '_'+str(period)+'_'+str(freq)

def teamrec(p):
    global rp
    issuecreatedate = dt.datetime.strptime(issueinfo.loc[p['issuekey']]['createdate'], '%Y-%m-%d')
    temprp = rp.copy()
    if filter:
        for i in rp:
            for j in rp[i]:
                if not isUserActive(j,issuecreatedate ,p['issuekey'],period,freq):
                    rp[i].remove(j)
    rp_temp = {}
    rp_temp['assignee'] = [p['assignee']]
    availableFlag = True
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
    rp = temprp
    if not availableFlag:
        return None
    #Get recommend team
    team = maxlogit(1000,rp_temp,0.05,teamStrengthCost,p['context'],p['components'],issuekey=p['issuekey'])
    team = format_output(team,RANK)
    return {'issue': p['issuekey'], 'r': team}


# In[ ]:

individual = False
missingrole = 'tester1'

if individual:
    print('role: '+missingrole)
    with open(filepathhelper.path(dataset,'actual_team.json')) as json_file:
        actual = pd.DataFrame(json.load(json_file))
        actual.set_index('issue',inplace=True)
print(dataset)
random.seed(123)
outdata = {} 
RANK=100
inputname = filepathhelper.path(dataset,'input_test.json')

filesuffixname = '_RECAST_'
if dataset.endswith('_hitnohit'):
    filesuffixname = filesuffixname + 'hitnohit_'
filesuffixname = filesuffixname + dataset.replace('_hitnohit','').lower()

outputname = 'output'+filesuffixname+filterstr+'.json'
NUMTHREAD = 30
print('NUMTHREAD: '+str(NUMTHREAD))

df_feature = {'issuekey':[],'rank':[],'cost':[]}
with open(inputname) as json_file:
    data = json.load(json_file)
    with mp.Pool(NUMTHREAD) as p:
 #       multi_out = p.imap(teamrec,data,chunksize=1)
        multi_out = tqdm(p.imap(teamrec,data,chunksize=1),total=len(data))
        temp = [i for i in multi_out]
    result = []
    for i in temp:
        if i is not None:
            result.append(i)
    for i in result[0]['r'][0]['features']:
        df_feature[i]=[]
    for res in result:
        issuekey = res['issue']
        recs = res['r']
        for r in recs:
            df_feature['issuekey'].append(issuekey)
            df_feature['rank'].append(r['rank'])
            df_feature['cost'].append(r.pop('cost'))
            features = r.pop('features')
            for f in features:
                df_feature[f].append(features[f])
    df_feature = pd.DataFrame(df_feature)
    df_feature.to_csv('recteam_feature'+filesuffixname+filterstr+'.csv')
    #save to json file
    saveOutput(outputname)



#

