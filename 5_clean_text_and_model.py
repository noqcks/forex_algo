import pandas as pd
import numpy as np
import re
import scipy

import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics

### STEPS ###
# 1. tokenize text
# 2. remove stopwords
# 3. discard if words not in wordnet
# 4. discard if words first hypernym not available
# 5. create feature vector of word hypernyms
# 6. assign tfidf weights to feature vector
# 7. calculate sentiment sumscores on words
# 8. multiply sumscore vector by tfidf weights vector
# 9. store tfidf feature vector
# 10. store tfidf*sumscore vector

news_df = pd.read_csv('news/MarketWatch-Combined_pn.csv')

### 1. TOKENIZE TEXT ###
### 2. REMOVE STOPWORDS ###
"""
This is where we remove punctuation and whitespace and also stop words
that have low informational content.
"""
# loading stopwords
stop = set(stopwords.words('english'))

def normalize_text(headline):
    # removing stopwords
    arr = [i for i in nltk.word_tokenize(headline.lower()) if i not in stop]

    # remove symbols and numbers
    str = " ".join(arr)
    str = re.sub('[^A-Za-z\s]+', '', str)
    str = re.sub("\s\s+", " ", str)

    return str

news_df['headline'] = news_df['headline'].apply(normalize_text)
# print(news_df['headline'])

### 3. DISCARD IF NOT IN WORDNET ###
### 4. DISCARED IF HYPERNYM NOT AVAILABLE ###
### 5. CREATE FEATURE VECTOR OF WORD HYPERNYMS ###

# replace words with hypernyms
def hypernym_replace(headline):
    arr = []
    for word in headline.split():
        # check if word exists in wordnet
        if wn.synsets(word) != []:
            # check if word has hypernyms
            if wn.synsets(word)[0].hypernyms() != []:
                arr.append(wn.synsets(word)[0].hypernyms()[0]._name)
    array = " ".join(arr)
    return array

news_df['headline'] = news_df['headline'].apply(hypernym_replace)
# print(news_df['headline'])

### 5. CREATE FEATURE VECTOR OF WORD HYPERNYMS ###
### 6. ASSIGN TFIDF WEIGHTS TO FEATURE VECTOR ###
vectorizer = TfidfVectorizer()
news_df['tfidf'] = vectorizer.fit_transform(news_df['headline'])
print(news_df['headline'][0])

np.set_printoptions(threshold=np.inf)

### 7. CALCULATE SENTIMENT SUMSCORES ON WORDS ###
# create a one-hot encoding feature vector of word sentiments
# sentiment sum score --> sentiment_sum = pos_sentiment_score + neg_sentiment_score

def remove_periods(df):
    arr = []
    for word in df.split():
        the_real = word.split('.', 1)[0]
        arr.append(the_real)
    return " ".join(arr)

test_df = news_df['headline'].apply(remove_periods)
vectorizer = TfidfVectorizer()
news = vectorizer.fit_transform(test_df)

# tfidf * sentiment_sum_score
cx = scipy.sparse.coo_matrix(news)
for i,j,v in zip(cx.row, cx.col, cx.data):
    # find original hypernyms
    regex=re.compile("%s.*" % vectorizer.get_feature_names()[j])
    word = [m.group(0) for l in news_df['headline'][i].split() for m in [regex.search(l)] if m][0]

    # get sum sentiment score
    try:
        breakdown = swn.senti_synset(word)
        sum_sentiment = breakdown.pos_score() + breakdown.neg_score()
    except:
        sum_sentiment = 0
    tfidf_score = news[i,j]

    # update original csr_matrix
    news[i,j] = tfidf_score  * sum_sentiment

# this is the tfidf * sentiment_sum_score matrix
# print(news)

# drop all zero values from the csr matrix
news = news[news.getnnz(1)>0]


# drop all rows in original df if they don't exist in the tfidf*senti matrix

print(news_df.shape)
del_array = []

for index, row in news_df.iterrows():
    try:
        news[index]
    except:
        del_array.append(index)

news_df = news_df.drop(news_df.index[del_array])

print(news_df.shape)

# print(news_df.shape)
# print(news_df)
# print(news)

news_df['senti_tfidf'] = news
news_df['label'].isnull().sum()

news = news[pd.notnull(news_df['label'])]

# split data into test and train
from sklearn.model_selection import train_test_split
from sklearn import svm
import datetime as dt

X_train, X_test, y_train, y_test = train_test_split(news, news_df['label'], test_size=0.15, random_state=42)

# train our model
param_C = 5
param_gamma = 0.05
classifier = svm.SVC(C=param_C,gamma=param_gamma)

start_time = dt.datetime.now()
print('Start learning at {}'.format(str(start_time)))
classifier.fit(X_train, y_train)
end_time = dt.datetime.now()
print('Stop learning {}'.format(str(end_time)))
elapsed_time= end_time - start_time
print('Elapsed learning {}'.format(str(elapsed_time)))

# get some accuracy
expected = y_test
predicted = classifier.predict(X_test)

print("Classification report for classifier %s:\n%s\n"
      % (classifier, metrics.classification_report(expected, predicted)))

cm = metrics.confusion_matrix(expected, predicted)
print("Confusion matrix:\n%s" % cm)

print("Accuracy={}".format(metrics.accuracy_score(expected, predicted)))
