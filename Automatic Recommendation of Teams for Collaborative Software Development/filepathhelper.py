#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import sys


# In[ ]:


def path(dataset,filename):
    curdir = os.getcwd()
    while 'Files' not in os.listdir(curdir):
        curdir = os.path.dirname(curdir)
    return os.path.join(curdir,'Files',dataset,filename)
    

#import os
#import sys
#curdir = os.getcwd()
#while 'filepathhelper.py' not in os.listdir(curdir):
#        curdir = os.path.dirname(curdir)
#sys.path.append(curdir)
#import filepathhelper