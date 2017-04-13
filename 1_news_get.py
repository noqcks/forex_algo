from eventregistry import *
import csv
import json
import pandas as pd

API_KEY = os.environ.get('EVENT_REGISTRY_API_KEY')
er = EventRegistry(apiKey = API_KEY)


# datelist days between 2015-01-01 and 2017-03-01
datelist = pd.bdate_range('2010-04-01', '2017-03-22').tolist()

# get all news from marketwatch
for date in datelist:
  datetime = pd.to_datetime(date)
  print datetime.date()

  q = QueryArticlesIter(
    # sourceUri = er.getNewsSourceUri("www.marketwatch.com"),
    dateStart = datetime.date(),
    dateEnd = datetime.date()
  )
  file = open("news/MarketWatch_Headlines-" + unicode(datetime.date()) + ".csv", "wb+")
  f = csv.writer(file, delimiter=',')
  f.writerow(["headline", "datetime"])

  for news in q.execQuery(er, sortBy = "date"):
    #print news
    if 'dateTime' in news:
      line = [news["title"].encode('ascii', 'ignore'), news["dateTime"]]
      print line
      f.writerow(line)

  file.close()


