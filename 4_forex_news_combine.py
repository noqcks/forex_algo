import pandas as pd
from datetime import datetime, timedelta
from pandas import Series
import numpy as np


# In this script we will take all news headlines as outputted by new_combine.py
# mash them into a 2 hour period

# This two hour period needs to be 1 hour offset from the 2 hour period of the forex
# prices.

news_df = pd.read_csv('news/MarketWatch-Combined.csv')
news_df.set_index('datetime', inplace=True)

# convert datetime to DateTimeIndex
news_df.index = pd.to_datetime(news_df.index)

# print news_df

fs = dict(Open='first', Close='last', Max='max')
ag = dict(Ask=fs, Bid=fs)
# offset by 1 hour from forex data
gp = pd.Grouper(freq='2H', base=1)
news_df = news_df.groupby(gp).sum()

f_df = pd.read_csv('USDCAD-2017_03_01-2017_03_17_grouped.csv')

# Create new column named Labels
sLength = len(news_df)
strs = ["" for x in range(sLength)]
news_df = news_df.assign(label=Series(strs).values)

# labels = []
for index, row in f_df.iterrows():
  # calculate positive or negative price change over 2 hours
  p_or_n = row['Close Bid'] - f_df.iloc[index-1]['Close Bid']

  # time offset for news
  dt = datetime.strptime(row['datetime'], '%Y-%m-%d %H:%M:%S')
  news_dt = dt - timedelta(hours=1)

  # set P when change over last two hours > 0
  if p_or_n > 0:
    news_df.set_value(news_dt, 'label', 'P')
  # set N when change over last two hours <= 0
  elif p_or_n <= 0:
    news_df.set_value(news_dt, 'label', 'N')

news_df.reset_index(level=0, inplace=True)
news_df.to_csv('news/MarketWatch-Combined_pn.csv', index=False)
