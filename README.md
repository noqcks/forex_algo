# Sentiment Based FOREX Algo

This is still technically a work in progress until I can find enough headline
data to validate my algo.

This will try predict FOREX market movements from headline data.

1. gets headline data from eventregistry

2. gets forex data from dukascopy

3. transforms headline data and associates it with forex data so that for every
2H period a string of headline information will have a P (pos) or N (neg) rating
based on forex data. There is a 1H offset between the forex data and headline data
so that we give the market time to converge.

4. this is where we clean the headline data and transform it. We take out low
information words and symbols, get word hypernyms, and then apply a sentiment score
to each word. We transform the hypernyms into a tfidf vector and then multiply our
tfidf scores by the sentiment sum scores we got earlier.

 The sentiment sum score is defined as:
 ```
sentiment_sum_score = word_negative_sentiment + word_positive_sentiment
```

5. this is where we apply a machine learning classification model (SVM) that will
try predict price movements from the headline vectors.

## Config

You can alter config settings in config.ini

```
start_date: the start date you want to analyze
end_date: the end date you want to analyze
er_api_key: the API key for http://eventregistry.org/
currency_pair: the currency pair you would like to try predict
```

## Running

```
./run.sh
```


## Requirements

```
pip install -r requirements.txt
```
