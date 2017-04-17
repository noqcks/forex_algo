import pandas as pd
import nltk
import scipy
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle


############################################
### 4. CLEAN AND TRANSFORM HEADLINE TEXT ###
############################################

##################################################################

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

##################################################################

news_df = pd.read_csv('input/headlines_pn.csv')

###########################
### 1. TOKENIZE TEXT ######
### 2. REMOVE STOPWORDS ###
###########################

##
# This is where we remove punctuation and whitespace and also stop words
#that have low informational content.
##

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

##################################################
### 3. DISCARD IF NOT IN WORDNET #################
### 4. DISCARED IF HYPERNYM NOT AVAILABLE ########
### 5. CREATE FEATURE VECTOR OF WORD HYPERNYMS ###
##################################################

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

##################################################
### 5. CREATE FEATURE VECTOR OF WORD HYPERNYMS ###
### 6. ASSIGN TFIDF WEIGHTS TO FEATURE VECTOR ####
##################################################

def remove_periods(df):
    arr = []
    for word in df.split():
        the_real = word.split('.', 1)[0]
        arr.append(the_real)
    return " ".join(arr)

tfidf = news_df['headline'].apply(remove_periods)
vectorizer = TfidfVectorizer()
headline_tfidf = vectorizer.fit_transform(tfidf)

#################################################
### 7. CALCULATE SENTIMENT SUMSCORES ON WORDS ###
#################################################

##
# sentiment_sum_score = pos_sentiment_score + neg_sentiment_score
##

# tfidf * sentiment_sum_score
cx = scipy.sparse.coo_matrix(headline_tfidf)
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
    tfidf_score = headline_tfidf[i,j]

    # update original csr_matrix
    headline_tfidf[i,j] = tfidf_score  * sum_sentiment

# drop all zero values from the csr matrix
headline_tfidf = headline_tfidf[headline_tfidf.getnnz(1)>0]


# drop all rows in original df if they don't exist in the tfidf*senti matrix
del_array = []
for index, row in news_df.iterrows():
    try:
        headline_tfidf[index]
    except:
        del_array.append(index)

news_df = news_df.drop(news_df.index[del_array])

headline_tfidf = headline_tfidf[pd.notnull(news_df['label'])]

with open('input/headline_tfidf.dat', 'wb') as outfile:
    pickle.dump(headline_tfidf, outfile, pickle.HIGHEST_PROTOCOL)

news_df.to_csv('input/headline_pn_clean.csv',index=False)
