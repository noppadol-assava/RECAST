
# This code finally calculate the positive and negative sentiment score of each comment
# It tokenize each sentence in each comments, clean it and then calculate its sentiment 
# by using sentistrength library, then find the average if sentence sentiment
# (Sentence with natural sentiment will not be included)

#command python sentiment_token.py Moodle moodle_comment.csv moodle_tag.csv

from sentistrength import PySentiStr
from textblob import TextBlob
import re
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from textblob import Word
import pandas as pd
from nltk.tokenize import sent_tokenize
#tqdm loading
from datetime import datetime
from pair_score import calculatePairScore
import os
import sys
NUMTHREAD = 20
curdir = os.getcwd()
while 'filepathhelper.py' not in os.listdir(curdir):
        curdir = os.path.dirname(curdir)
sys.path.append(curdir)
import filepathhelper
from tqdm import tqdm
import multiprocessing as mp


senti = PySentiStr()
#    senti.setSentiStrengthPath('C:\ProgramData\Anaconda3\Lib\site-packages\sentistrength\SentiStrength.jar')
#    senti.setSentiStrengthLanguageFolderPath('C:\ProgramData\Anaconda3\Lib\site-packages\sentistrength\\')
senti.setSentiStrengthPath('/home/waraleetan/ming/lib/python2.7/site-packages/sentistrength/SentiStrength.jar')
senti.setSentiStrengthLanguageFolderPath('/home/waraleetan/ming/lib/python2.7/site-packages/sentistrength/')
    

def cleanData(text):
    #remove [~]
    result = re.sub("\\[~.*?\\]", "", text)

    #remove{code}
    result = re.sub(r'^{code(.+){code}', ' ', result)
    
    #remove{function name}
    result = re.sub(r'\s\w+\(\)', ' ', result)
    
    #remove {noformat}
    result = re.sub(r'{noformat}.+{noformat}', ' ', result)
    
    #remove [...]
    result = re.sub(r'\s\[.+\]\s',' ',result)
    
    # remove URL
    result = re.sub(r"http\S+", "", result)

    # Numbers removing
    result = re.sub(r'\d+', '', result)

    # To lowercase
    result = result.lower()

    # Remove number
    result = re.sub("^\d+\s|\s\d+\s|\s\d+$", " ", result )

    # remove punctuation but not remove emoji
    result = result.translate(str.maketrans('', '', string.punctuation))
    result = re.sub(r'(?<=\w)[^\s\w](?![^\s\w])', '', result)

    # remove white space
    result = result.strip()

    # remove stopwords
    stop_words = set(stopwords.words('english'))
    from nltk.tokenize import word_tokenize
    tokens = word_tokenize(result)
    result = [i for i in tokens if not i in stop_words]

    # stemming
    #     stemmer= PorterStemmer()
    #     newResult = []
    #     for word in result:
    #         newResult.append(stemmer.stem(word))
    #     print(newResult)
    return result



def sentence_sentiment(data):
    commentid = data['commentid']
    message = data['message']
    #print(commentid, message)
    try:
        sentence = sent_tokenize(message)
    except:
        print('error cannot tokenize')
    sentimentp = 0
    sentimentn = 0          
    pos = []
    neg = []
    for s in sentence:
        c = cleanData(s)
        cs = ' '.join(word for word in c if len(word)<20)
        if len(c) != 0:
            try:
                score = senti.getSentiment(cs, score='binary')
                p = score[0][0]
                n = score[0][1]
                if p != 1 or n != -1:
                    #normalize
                    pos.append(p/5)
                    neg.append(n/5)
            except:
                print("cannot get sentiment")
        
        if len(pos) != 0 and len(neg) != 0:
            sentimentp = sum(pos)/len(pos)
            sentimentn = sum(neg)/len(neg)
        if len(pos) == 0:
            sentimentp = 0
        if len(neg) == 0:
            sentimentn = 0
    
#    print('commentid',commentid,'positivescore', str(sentimentp), 'negativescore',str(sentimentn))
    return {'commentid':commentid,'positivescore': sentimentp, 'negativescore':sentimentn}
    
def filterTrain(commentissuekey, train):
    print(commentissuekey['issuekey'])
    print(train['issuekey'])
    validid = commentissuekey[commentissuekey.issuekey.isin(train.issuekey)]
    return set(validid['commentid'].values)
    


def comment_sentiment(dataset,commentFileName,tagFileName, commentissuekey, train):  
    out = "sentiment_temp_"+dataset+".csv"
    commentFile = '/home/waraleetan/Files/Atlassian/atlassian_comment.csv'#filepathhelper.path(dataset,commentFileName)
    tagPair = '/home/waraleetan/Files/Atlassian/jira_tags.csv'#filepathhelper.path(dataset,tagFileName)
    trainfile = '/home/waraleetan/Files/Atlassian/jira_trainissuekey.csv'#filepathhelper.path(dataset,train)
    commentissuekeyfile = '/home/waraleetan/Files/Atlassian/jira_issuekey_comments.csv'
    output_score = out
    

    print(commentFile, tagPair)
    data = pd.read_csv(commentFile )
    data.set_index('commentid', inplace=True)

    tagcomment = pd.read_csv(tagPair , encoding='iso-8859-1')
    #tagcomment = tagcomment[:100]
    
    commentissuekey = pd.read_csv(commentissuekeyfile , encoding='iso-8859-1', sep = ';')
    train = pd.read_csv(trainfile)# , encoding='iso-8859-1')
#    train = train[:100]
    
    invalid = []
    allmessage = []

    count = 0
    
    print("Number of tagging: ",len(tagcomment))
    print("Number of comments: ",len(data))    
    
    print('filter train commentid')
    print(commentissuekey)
    trainid = filterTrain(commentissuekey, train)
    
    print('train keys: ',str(len(trainid)))
    
#    for index, row in tagcomment.iterrows():
#        if row['commentid'] in trainid:#train['commentid'].values:
#            try:
#                if row['tagger'] != 'jira-bot' and row['taggee'] != 'jira-bot':
#                    message = data.loc[row['commentid'], 'message']      
#                    allmessage.append({'commentid': row['commentid'], 'message': message})
#            except:
#                invalid.append(row['commentid'])
    tagcomment = tagcomment.drop(tagcomment[tagcomment.tagger == 'jira-bot'].index)
    tagcomment = tagcomment.drop(tagcomment[tagcomment.taggee == 'jira-bot'].index)
    
    tagcommentid = list(set(tagcomment['commentid']))
    
    for i in tqdm(range(len(tagcommentid))):
         if tagcommentid[i] in trainid:#train['commentid'].values:
            try:
                message = data.loc[tagcommentid[i], 'message']      
                allmessage.append({'commentid': tagcommentid[i], 'message': message})
            except:
                invalid.append(tagcommentid[i])       
        
    print('Number of all message:', str(len(allmessage)))
    print('Number of invalid comment',str(len(set(invalid))))
    
    with mp.Pool(NUMTHREAD) as p:
        multi_out = tqdm(p.imap(sentence_sentiment, allmessage, chunksize = 1), total = len(allmessage))
        #print(multi_out)
        temp = [i for i in multi_out]
    
    result = []
    for i in temp:
        if i is not None:
            result.append(i)

    resultdf = pd.DataFrame.from_records(result)
    resultdf.to_csv(output_score, index=False)
    
    return resultdf
    
comment_sentiment('Atlassian','atlassian_comment.csv','jira_tags.csv', 'jira_issuekey_comments','jira_trainissuekey.csv')