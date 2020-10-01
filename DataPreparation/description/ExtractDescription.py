#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
import json
import mysql.connector
from tqdm import tqdm
import time
import re
import argparse
import getpass
from datetime import datetime
import numpy as np
import pandas as pd


# # For command line code

# In[2]:


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", type=str, default="",
	help="jira project")
ap.add_argument("-path", "--path", type=str, default="",
	help="path to dataset directory")
args = vars(ap.parse_args())


# # Required Function

# In[4]:


def setMoodle():
    global datasetloc
    datasetloc='MoodleDataSet'


# In[5]:


def setAtlassian():
    global datasetloc
    datasetloc='AtlassianDataSet'
	
def setApache():
    global apiaddress
    global participantField
    global integratorField
    global peerreviewerField 
    global componentwatcherField 
    global testerField
    global datasetloc
#     apiaddress='tracker.moodle.org'
#     participantField='customfield_10020'
#     integratorField='customfield_10110'
#     peerreviewerField='customfield_10118' 
#     componentwatcherField='customfield_14214' 
#     testerField='customfield_10530'
    datasetloc='ApacheDataSet'

# In[11]:


def stringToDT(string):
    string = string.replace('T',' ')
    string = string[0:19]
    string = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
    return string


# # Setting up parameters

# In[6]:


dbname=''
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
# db = connectToDB()


# In[7]:


issuepath = os.path.join(path,datasetloc,'issues')


# # Extract Process
# 

# In[15]:

pbar = tqdm(total=len(os.listdir(issuepath)))
issues = []
des = []
for i in os.listdir(issuepath):
    if i.endswith('_CL.json'):
        issuekey = i[:-8]
        with open(os.path.join(issuepath,i), encoding='utf-8') as json_file:
            data = json.load(json_file)
            field = data['fields']
            if 'description' in field:
                descript = field['description']
                if descript is None:
                    des.append(descript)
                else:
                    des.append("%r"%descript)
                issues.append(issuekey)
        pbar.update(1)
pbar.close()
desdf = pd.DataFrame({'issuekey':issues,'description':des})
desdf.to_csv(args['dataset']+'_description.csv',index = False)


# In[ ]:




