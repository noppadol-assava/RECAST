# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 15:04:11 2020

@author: windows
"""

#python extract_interaction.py Moodle moodle_comment.csv moodle_tag.csv issue_comment.csv trainissuekey.csv
import sys
import os
import pandas as pd
import sentiment_token as sentiment
from pair_score import calculatePairScore,  calculatePairScoreFilter
from globalTrustMatrix import calculateTrustMatrix
curdir = os.getcwd()
while 'filepathhelper.py' not in os.listdir(curdir):
        curdir = os.path.dirname(curdir)
sys.path.append(curdir)
import filepathhelper


if __name__== "__main__":
    dataset = ''
    commentFileName = ''
    tagFileName = ''
    issuecommentFile = ''
    trainsetFile = ''
    print(len(sys.argv))
    if len(sys.argv) != 6:
        dataset = "Atlassian"
        commentFileName ="/home/waraleetan/sentiment/data/Moodle_comments.csv"
        tagFileName = '/home/waraleetan/Files/Atlassian/jira_tags.csv'
        issuecommentFile = "issue_comment.csv"
        trainsetFile = "trainissuekey.csv"
    else:
        dataset = sys.argv[1]
        commentFileName = sys.argv[2]
        tagFileName = sys.argv[3]
        issuecommentFile = sys.argv[4]
        trainsetFile = sys.argv[5]
        
#Filter train set
#    issuecomment = pd.read_csv(filepathhelper.path(dataset, issuecommentFile), encoding='iso-8859-1', sep=';')
#    trainset = pd.read_csv(filepathhelper.path(dataset, trainsetFile), encoding='iso-8859-1')
#    traincomment = pd.merge(trainset, issuecomment, left_on='issuekey', right_on='issuekey', how='inner')     
    traincomment = ""
    
#    find sentiment of each comment
#   It  returns dataframe of comments
    # sentiment_score = sentiment.comment_sentiment(dataset, commentFileName, tagFileName, traincomment)
    
    sentiment_score = pd.read_csv('sentiment_temp_Atlassian.csv', encoding='iso-8859-1')
#   Calculate average sentiment between each pair
    calculatePairScore(dataset, tagFileName, sentiment_score, traincomment,"pair_score_"+dataset+".csv")
    #calculatePairScoreFilter(dataset, tagFileName, sentiment_score, traincomment,"pair_score_"+dataset+".csv")

#   propergate Trust   
    calculateTrustMatrix("pair_score_"+dataset+".csv","global_pair_score.csv")
    
# Then we will get file name global_pair_score.csv to retrieve score