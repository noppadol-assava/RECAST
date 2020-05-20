#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import json
import mysql.connector
from tqdm import tqdm
import time
import re
import argparse
import getpass


# # For command line code

# In[2]:


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
    global dbname
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


# In[5]:


def setAtlassian():
    global apiaddress
    global participantField
    global integratorField
    global peerreviewerField 
    global componentwatcherField 
    global testerField
    global datasetloc

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

    datasetloc='ApacheDataSet'


# # Setting up parameters

# In[6]:


apiaddress=''
dbname=''
participantField=''
integratorField=''
peerreviewerField='' 
componentwatcherField='' 
testerField=''
path = args['path']
datasetloc=''


# # Setup dataset and database

# In[8]:


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


# In[7]:


issuepath = os.path.join(path,datasetloc,'issues')
commentpath = os.path.join(path,datasetloc,'comments')
developmentpath = os.path.join(path,datasetloc,'developments')


# # Extract Developer from JSON files and Keep in MYSQL 
# 

# In[15]:

count_commit = 0
cursor = db.cursor()
pbar = tqdm(total=len(os.listdir(issuepath)))
for i in os.listdir(issuepath):
    if i.endswith('_CL.json'):
#        cursor = db.cursor()
        issuekey = i[:-8]
        with open(os.path.join(issuepath,i), encoding='utf-8') as json_file:
            data = json.load(json_file)
            field = data['fields']
            #if 'components' in field:
            try:
                components = field['components']
                for comp in components:
                    cname = comp['name']
                    prefix = i.split('-')[0]
                    sql = "INSERT INTO component (`issuekey`, `component`) VALUES " + " (%s,%s);";
                    val = (issuekey,prefix+'_'+cname)
                    try:
                        cursor.execute(sql, val)
                    except mysql.connector.IntegrityError:
                        donothing=0
#             title = field['summary'] if 'summary' in field and field['summary'] is not None else None
                count_commit=count_commit+1
                if count_commit == 1000:
                    db.commit()
                    count_commit=0
            except KeyError:
                donothing =0
#        cursor.close()
        pbar.update(1)
if count_commit !=0:
    db.commit()
    count_commit=0
pbar.close()
cursor.close()
db.close()


# In[ ]:




