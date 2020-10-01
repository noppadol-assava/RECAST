#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import traceback
import base64
import json
import os
import time
import mysql.connector
from tqdm import tqdm
from requests.auth import HTTPBasicAuth
import argparse
import getpass


# In[ ]:
apiuser = 'user'
apipass = 'pass'

ap = argparse.ArgumentParser()
ap.add_argument("-db", "--dbname", type=str, default="",
	help="name of database")
ap.add_argument("-u", "--username", type=str, default="root",
	help="username of mysql")
ap.add_argument("-d", "--dataset", type=str, default="",
	help="jira project")
ap.add_argument("-path", "--path", type=str, default="",
	help="path to dataset directory")
	
args = vars(ap.parse_args())


# # Required Function

# In[ ]:


def RecordCollectedUser(username,note):
    cursor = db.cursor()
    query = "INSERT INTO temp_collecteduser (`username`, `Note`) VALUES (%s,%s);";
    val = (username,note)
    try:
        cursor.execute(query , val)
        db.commit()
    except Exception:
        print(traceback.format_exc())
    cursor.close()


# In[ ]:


def CollectUser(username):
    r = requests.get(apiaddress+'/rest/api/2/user/?username='+username+'&expand=groups,applicationRoles',auth=HTTPBasicAuth(apiuser, apipass))
    if r.status_code !=200:
        global requesterror
        requesterror = requesterror+1
    else:
        with open(os.path.join(userpath,username+'_user.json'), 'w') as json_file:  
            json.dump(r.json(), json_file)


# In[3]:


def connectToDB():
    return mysql.connector.connect(
        host="localhost",
        user=args['username'],
        passwd=getpass.getpass('Password:'),
        database=args['dbname']
    )


# In[4]:


def setMoodle():
    global apiaddress
    global participantField
    global integratorField
    global peerreviewerField 
    global componentwatcherField 
    global testerField
    global datasetloc

    apiaddress='http://tracker.moodle.org'
    participantField='customfield_10020'
    integratorField='customfield_10110'
    peerreviewerField='customfield_10118' 
    componentwatcherField='customfield_14214' 
    testerField='customfield_10011'
    datasetloc='MoodleDataSet'


# In[5]:


def setAtlassian():
    global apiaddress
    global participantField
    global integratorField
    global peerreviewerField 
    global componentwatcherField 
    global testerField
    global datasetloc
    apiaddress='jira.atlassian.com'
#    participantField='customfield_10020'
#    integratorField='customfield_10110'
#    peerreviewerField='customfield_10118' 
#    componentwatcherField='customfield_14214' 
#    testerField='customfield_10530'
    datasetloc='AtlassianDataSet'


# In[ ]:


def setApache():
    global apiaddress
    global participantField
    global integratorField
    global peerreviewerField 
    global componentwatcherField 
    global testerField
    global datasetloc
    apiaddress='http://issues.apache.org/jira'
#     participantField='customfield_10020'
#     integratorField='customfield_10110'
#     peerreviewerField='customfield_10118' 
#     componentwatcherField='customfield_14214' 
#     testerField='customfield_10530'
    datasetloc='ApacheDataSet'


# # Setting up parameters

# In[ ]:


apiaddress=''
dbname=''
path = args['path']
datasetloc=''
apiuser=''
apipass=''


# In[ ]:


if args['dataset']=='Moodle':
    setMoodle()
elif args['dataset']=='Atlassian':
    setAtlassian()
elif args['dataset']=='Apache':
    setApache()
else:
    print('Invalid Dataset!!!')
    exit()
db = connectToDB()
issuepath = os.path.join(path,datasetloc,'issues')
commentpath = os.path.join(path,datasetloc,'comments')
developmentpath = os.path.join(path,datasetloc,'developments')
userpath = os.path.join(path,datasetloc,'users')


# # Collect Data

# In[ ]:


query = 'Select distinct username from collect_user where username not in (select username from temp_collecteduser)';


# In[ ]:


mycursor = db.cursor()

mycursor.execute(query)

results = mycursor.fetchall()
requesterror =0
error = 0
pbar = tqdm(total=len(results))
for username, in results:
    check = 0
    try:
        CollectUser(username)
        time.sleep(.065)
        check =1
    except Exception:
        print(traceback.format_exc())
        time.sleep(10)
        check =0
    if check==1:
        RecordCollectedUser(username,'Collected')
    else:
        error=error+1
    pbar.update(1)
pbar.close()


# In[36]:


print('Error occure: '+str(error))


# In[ ]:


print('Request error occure: '+str(requesterror))


# In[ ]:


mycursor.close()
db.close()


# In[3]:




