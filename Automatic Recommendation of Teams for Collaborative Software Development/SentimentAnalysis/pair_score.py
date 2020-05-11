# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 14:24:22 2020

@author: windows
"""

# This code group and calculate average positive and negative comments between each pair

import pandas as pd
import re
import string
import numpy as np
import sys
import os
import sys
curdir = os.getcwd()
while 'filepathhelper.py' not in os.listdir(curdir):
        curdir = os.path.dirname(curdir)
sys.path.append(curdir)
import filepathhelper

def filterTrainSet(commentscore, train):
    commentid = []
    positivescore = []
    negativescore = []
    print(len(train['commentid'].values),len(commentscore['commentid'].values) )
    print(len( set(commentscore['commentid'].values).intersection(set(train['commentid'].values))))
    for i in range(len(commentscore)):
        if commentscore['commentid'][i] in train['commentid'].values:
            commentid.append(commentscore['commentid'][i])
            positivescore.append(commentscore['positivescore'][i])
            negativescore.append(commentscore['negativescore'][i])
            
    datadict = {'commentid': commentid, 'positivescore': positivescore,'negativescore': negativescore}
    traincomment = pd.DataFrame(datadict)
    traincomment = traincomment[['commentid', 'positivescore','negativescore']]
    return traincomment 
    

def calculatePairScore(dataset, tagpair, commentscore, train, outfile):

    #train = pd.read_csv(filepathhelper.path(dataset, train), encoding='iso-8859-1')
    tagcomment = pd.read_csv(filepathhelper.path(dataset, tagpair), encoding='iso-8859-1')

    #remove white space at beginning
    tagcomment['tagger'] = tagcomment.tagger.str.lstrip()
    tagcomment['taggee'] = tagcomment.taggee.str.lstrip()

    #remove user null
    tagcomment= tagcomment[tagcomment['tagger']!=' ']
    tagcomment= tagcomment[tagcomment['taggee']!=' ']

    #remove user that contains / (error from extract tagger and taggee)
    tagcomment= tagcomment[~tagcomment.tagger.str.contains('/',na=False)]
    tagcomment= tagcomment[~tagcomment.taggee.str.contains('/',na=False)]

    check = ~tagcomment.tagger.str.isdigit()
    #remove user all digit
    tagcomment= tagcomment[check]
    #check = ~tagcomment.taggee.str.isdigit()
    #tagcomment = tagcomment[check ]
    
#    commentscore = filterTrainSet(commentscore,train)
#    commentscore = commentscore.drop_duplicates()
#    print(commentscore)
    
    
    #tagcomment = tagcomment.set_index('commentid').join(commentscore.set_index('commentid'))
    tagcomment = pd.merge(tagcomment, commentscore, left_on='commentid', right_on = 'commentid', how='inner')
    pair = tagcomment.groupby(['tagger', 'taggee']).agg({'positivescore': 'mean','negativescore': 'mean'})
    pair.reset_index().set_index(['tagger', 'taggee']).sort_index(level= 0).to_csv(outfile)
    
def calculatePairScoreFilter(dataset, tagpair, commentscore, train, outfile):

    #train = pd.read_csv(filepathhelper.path(dataset, train), encoding='iso-8859-1')
    tagcomment = pd.read_csv(filepathhelper.path(dataset, tagpair), encoding='iso-8859-1')
    
    commentscore = filterTrainSet(commentscore,train)
    commentscore = commentscore.drop_duplicates()
#    print(commentscore)
    
    
    #tagcomment = tagcomment.set_index('commentid').join(commentscore.set_index('commentid'))
    tagcomment = pd.merge(tagcomment, commentscore, left_on='commentid', right_on = 'commentid', how='inner')
    pair = tagcomment.groupby(['tagger', 'taggee']).agg({'positivescore': 'mean','negativescore': 'mean'})
    pair.reset_index().set_index(['tagger', 'taggee']).sort_index(level= 0).to_csv(outfile)

if __name__== "__main__":
    if len(sys.argv) == 4:  
        dataset = sys.argv[1]
        tagPair = sys.argv[2]
        commentSentiment = sys.argv[3]
        commentscore= pd.read_csv(commentSentiment , encoding='iso-8859-1')
        calculatePairScore(dataset,tagPair, commentscore, 'pair_score.csv')
        
#calculatePairScore('Moodle','tags.csv', pd.read_csv('sentiment_Moodle.csv', encoding='iso-8859-1'),'trainissuekey.csv', 'pair_score.csv')