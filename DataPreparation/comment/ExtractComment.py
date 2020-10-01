#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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


# In[ ]:


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", type=str, default="",
	help="jira project")
ap.add_argument("-path", "--path", type=str, default="",
	help="path to dataset directory")
args = vars(ap.parse_args())


# In[ ]:


def setMoodle():
    global datasetloc
    datasetloc='MoodleDataSet'
def setAtlassian():
    global datasetloc
    datasetloc='AtlassianDataSet'
def setApache():
    global datasetloc
    datasetloc='ApacheDataSet'


# In[ ]:


path = args['path']
datasetloc=''


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


# In[ ]:


commentpath = os.path.join(path,datasetloc,'comments')


# In[ ]:


cid = []
cmd = []
pbar = tqdm(total=len(os.listdir(commentpath)))
for i in os.listdir(commentpath):
    if i.endswith('_Comment.json'):
#         cursor = db.cursor()
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
#                     timecreate = stringToDT(comment['created'])
                    message = comment['body']
                    if message is None:
                        cmd.append(message)
                    else:
                        cmd.append("%r"%message)
                    cid.append(commentid)
                    
#                     tags = set(re.findall("\[~([^\]]+)\]", message))
#                     for tag in tags:
#                         sql = "INSERT INTO tags(`commentid`,`tagger`,`taggee`) VALUES (%s,%s,%s);";
#                         val = (commentid,username,tag)
#                         try:
#                             cursor.execute(sql, val)
#                         except mysql.connector.IntegrityError:
#                             print('error occured')
#                             donothing=0
#                     sql = "INSERT INTO comments(`issuekey`,`commentid`,`timecreated`) VALUES (%s,%s,%s);";
#                     val = (issuekey,commentid,timecreate)
#                     try:
#                         cursor.execute(sql, val)
#                     except (mysql.connector.IntegrityError,mysql.connector.errors.OperationalError) as e:
#                         print('error occured')
#             db.commit()
#         cursor.close()
        pbar.update(1)
pbar.close()


# In[ ]:


cmdf = pd.DataFrame({'commentid':cid,'message':cmd})
cmdf.to_csv(args['dataset']+'_comment.csv',index = False)

