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


def RecordCollectedIssue(issuekey,note):
    cursor = db.cursor()
    query = "INSERT INTO temp_collectedissue (`issuekey`, `Note`) VALUES (%s,%s);";
    val = (issuekey,note)
    try:
        cursor.execute(query , val)
        db.commit()
    except Exception:
        print(traceback.format_exc())
    cursor.close()


# In[ ]:


def CollectDevelopment(issuekey,issueid):
    r = requests.get('https://tracker.moodle.org/rest/dev-status/latest/issue/detail?issueId='+issueid+'&applicationType=github&dataType=repository',auth=HTTPBasicAuth(apiuser,apipass))
    if r.status_code !=200:
        global requesterror
        requesterror = requesterror+1
    else:
        with open(os.path.join(developmentpath,issuekey+'_development.json'), 'w') as json_file:  
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
    apiaddress='tracker.moodle.org'
    participantField='customfield_10020'
    integratorField='customfield_10110'
    peerreviewerField='customfield_10118' 
    componentwatcherField='customfield_14214' 
    testerField='customfield_10011'
    datasetloc='MoodleDataSet'


# # Setting up parameters

# In[ ]:


apiaddress=''
dbname=''
path = args['path']
datasetloc=''


# In[ ]:


if args['dataset']=='Moodle':
    setMoodle()
else:
    print('Invalid Dataset!!!')
    exit()
db = connectToDB()
issuepath = os.path.join(path,datasetloc,'issues')
commentpath = os.path.join(path,datasetloc,'comments')
developmentpath = os.path.join(path,datasetloc,'developments')


# # Collect Data

# In[ ]:


query = 'Select distinct issuekey,issueid from issue_id where issuekey not in (select issuekey from temp_collectedissue)';


# In[ ]:


mycursor = db.cursor()

mycursor.execute(query)

results = mycursor.fetchall()
requesterror =0
error = 0
pbar = tqdm(total=len(results))
for key,i in results:
    check = 0
    try:
        CollectDevelopment(key,i)
        time.sleep(.065)
        check =1
    except Exception:
        print(traceback.format_exc())
        time.sleep(10)
        check =0
    if check==1:
        RecordCollectedIssue(key,'Collected')
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

