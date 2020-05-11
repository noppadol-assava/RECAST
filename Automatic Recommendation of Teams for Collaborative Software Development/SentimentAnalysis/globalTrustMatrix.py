# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 22:52:53 2020

@author: windows
"""

#This code convert data from positive and negative sentiment of each pair in csv
#format into matrix and do operation to calculate global trust to propergate trust value
#The output will be the file which contains new values of positive and negative sentiment of all pairs
#Change input file and output file to run code

import pandas as pd
import numpy as np
import datetime

#def mul(X,Y):
#    result = [[0]*len(X) for _ in range(len(Y))]
#    if len(X) == len(Y):
#        for i in range(len(X)):
#       # iterate through columns of Y
#           for j in range(len(Y[0])):
#               # iterate through rows of Y
#               for k in range(len(Y)):
#                   result[i][j] += X[i][k] * Y[k][j]     
#    return result

def staticmul (k, mat):
    res = [[0]*len(mat) for _ in range(len(mat))]
    for i in range(len(mat)):
        for j in range(len(mat)):
            res[i][j] = k*mat[i][j]
    return res

def calculateTrustMatrix(pair_score_file, outfile):
    #-------------------------------input-----------------------------------------#
    #data = pd.read_csv("/home/waraleetan/jira_swteam_recommendation/sentiment/sentiout/pair_score_1.csv")
    #data = pd.read_csv("sentiout/pair_score_1.csv")
    data = pd.read_csv(pair_score_file)
    #data = data[:2]
    #-----------------------------------------------------------------------------#
    
    tagger = data['tagger']
    taggee = data['taggee']
    pos = data['positivescore']
    neg = data['negativescore']
    
    start = datetime.datetime.now()
    
    print('listing all members from tagger and taggee...')
    member = list(set().union(tagger,taggee))
    print(member)
    member.sort()
    
    #print(data)
    #print(member)
    
    numMem = len(member)
    
    P = [[0]*numMem for _ in range(numMem)]
    N = [[0]*numMem for _ in range(numMem)]
    print('Assign origin value into matrix...')
    
    for i in range(len(data)):
        taggerIndex = member.index(tagger[i])
        taggeeIndex = member.index(taggee[i])
        P[taggerIndex][taggeeIndex] = pos[i]
        N[taggerIndex][taggeeIndex] = -1*neg[i]
#        print(tagger[i], "(", taggerIndex, ") ", taggee[i], "(", taggeeIndex, ") = ", data['positivescore'][i], data['negativescore'][i])
        
    p = np.array(P)
    pt = p.transpose()
    
    n = np.array(N)
    nt = n.transpose()
    
    print('Calculating global trust...')
    
    #C = a1b + a2bt*b + a3bt + a4bbt
    a = [0.4,0.4,0,0.1]
    
    p1 = staticmul(a[0],p)
    p2 = staticmul(a[1] , pt.dot(p))
    p3 = staticmul(a[2],pt)
    p4 = staticmul(a[3] , p.dot(pt))
    pFinal = np.add(p1,np.add(p2, np.add(p3,p4)))
    
    pFinal = pFinal.tolist()
    
    n1 = staticmul(a[0],n)
    n2 = staticmul(a[1] , nt.dot(n))
    n3 = staticmul(a[2],nt)
    n4 = staticmul(a[3] , n.dot(nt))
    nFinal = np.add(n1,np.add(n2, np.add(n3,n4)))
    
    print(nFinal)
    nFinal = nFinal.tolist()
    
    taggerList = []
    taggeeList = []
    posscore = []
    negscore = []
    
    print('Transform into pairs...')
    
    for i in range(numMem):
        for j in range(numMem):
            if i!=j:
                if pFinal[i][j] != 0 or nFinal[i][j] != 0:
                    taggerList.append(member[i])
                    taggeeList.append(member[j])
                    posscore.append(pFinal[i][j])
                    negscore.append(nFinal[i][j])
    
    datadict = {'tagger': taggerList, 'taggee': taggeeList,'positivescore': posscore,'negativescore': negscore}
    commentSentiment = pd.DataFrame(datadict)
    commentSentiment = commentSentiment[['tagger', 'taggee','positivescore','negativescore']]
    
    #-------------------------------output-----------------------------------------#
    commentSentiment.to_csv(outfile, index=False)
    #------------------------------------------------------------------------------#
    
    end = datetime.datetime.now()
    timespend = end - start
    print(timespend)
    print('Matrix done')