from eventregistry import *
import csv
import json
import pandas as pd
import subprocess

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

############################
### 1. GET HEADLINE DATA ###
############################

###
# We will grab news headline data from eventregistry
###

er = EventRegistry(apiKey = config['DEFAULT']['er_api_key'])

# headline dates to get
datelist = pd.bdate_range(config['DEFAULT']['start_date'], config['DEFAULT']['end_date']).tolist()

headlines = []

# get headline data
for date in datelist:
  datetime = pd.to_datetime(date)

  q = QueryArticlesIter(
    # source is MarketWatch
    sourceUri = er.getNewsSourceUri("www.marketwatch.com"),
    dateStart = datetime.date(),
    dateEnd = datetime.date()
  )

  for news in q.execQuery(er, sortBy = "date"):
    if 'dateTime' in news:
      line = {'headline': news["title"].encode('ascii', 'ignore'), 'datetime': news["dateTime"]}
      headlines.append(line)

# create DataFrame
df = pd.DataFrame(headlines, columns=['headline', 'datetime'])

# save DataFrame as csv
df.to_csv('input/headlines.csv', index=False)


