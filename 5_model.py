import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn import svm
import datetime as dt
from sklearn import metrics

with open('input/headline_tfidf.dat', 'rb') as infile:
    news = pickle.load(infile)

news_df = pd.read_csv('input/headline_pn_clean.csv')

# split up our data
X_train, X_test, y_train, y_test = train_test_split(news, news_df['label'], test_size=0.15, random_state=42)

# set hyperparams
param_C = 5
param_gamma = 0.05
classifier = svm.SVC(C=param_C,gamma=param_gamma)

# train the model
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
