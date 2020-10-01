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
    global datasetloc
    datasetloc='MoodleDataSet'


# In[5]:


def setAtlassian():
    global datasetloc
    datasetloc='AtlassianDataSet'


# In[ ]:


def setApache():
    global datasetloc
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
db = connectToDB()


# In[7]:


commentpath = os.path.join(path,datasetloc,'comments')


# # Extract Process
# 

# In[15]:


pbar = tqdm(total=len(os.listdir(commentpath)))
for i in os.listdir(commentpath):
    if i.endswith('_Comment.json'):
        cursor = db.cursor()
        issuekey = i[:-13]
        with open(os.path.join(commentpath,i), encoding = "ISO-8859-1") as json_file:
            data = json.load(json_file)
            comments = data['comments']
            if data['total']>0:
                for comment in comments:
                    commentid = comment['id']
                    username=''
                    if 'author' in comment:
                        username = comment['author']['key']
                    timecreate = stringToDT(comment['created'])
                    message = comment['body']
                    tags = set(re.findall("\[~(.*?)\]", message))
                    for tag in tags:
                        sql = "INSERT INTO tags(`commentid`,`tagger`,`taggee`) VALUES (%s,%s,%s);";
                        val = (commentid,username,tag)
                        try:
                            cursor.execute(sql, val)
                        except:
                            print('error occured at'+issuekey)
                    sql = "INSERT INTO comments(`issuekey`,`commentid`,`timecreated`) VALUES (%s,%s,%s);";
                    val = (issuekey,commentid,timecreate)
                    try:
                        cursor.execute(sql, val)
                    except:
                        print('error occured at'+issuekey)
        cursor.close()
        pbar.update(1)
pbar.close()
db.commit()

# In[ ]:




