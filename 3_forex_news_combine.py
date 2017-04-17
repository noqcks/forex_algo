import pandas as pd
from datetime import datetime, timedelta
from pandas import Series
import numpy as np

# config
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
s_date = config['DEFAULT']['start_date']
e_date = config['DEFAULT']['end_date']
currency_pair = config['DEFAULT']['currency_pair']
file_name = "{0}-{1}-{2}".format(currency_pair, s_date.replace("-", "_"), e_date.replace("-", "_"))

#############################
### 3. COMBINE NEWS/FOREX ###
#############################

##
# We will take news headline data and FOREX data and combine then into one dataframe
# The news and forex data will be offset by 1H to account for market
# convergence (the time news is consumed to when the market reacts).
##

news_df = pd.read_csv('input/headlines.csv')
news_df.set_index('datetime', inplace=True)

# convert datetime to DateTimeIndex
news_df.index = pd.to_datetime(news_df.index)

fs = dict(Open='first', Close='last', Max='max')
ag = dict(Ask=fs, Bid=fs)
# offset by 1 hour from forex data
gp = pd.Grouper(freq='2H', base=1)
news_df = news_df.groupby(gp).sum()

forex_df = pd.read_csv('input/{0}_grouped.csv'.format(file_name))

# Create new column named Labels
sLength = len(news_df)
strs = ["" for x in range(sLength)]
news_df = news_df.assign(label=Series(strs).values)

for index, row in forex_df.iterrows():
    # calculate positive or negative price change over 2 hours
    p_or_n = row['Close Bid'] - forex_df.iloc[index-1]['Close Bid']

    # time offset for news
    dt = datetime.strptime(row['datetime'], '%Y-%m-%d %H:%M:%S')
    news_dt = dt - timedelta(hours=1)

    # set P when change over last two hours > 0
    if p_or_n > 0:
        news_df.set_value(news_dt, 'label', 'P')
    # set N when change over last two hours <= 0
    elif p_or_n <= 0:
        news_df.set_value(news_dt, 'label', 'N')

# drop first value because the P/N will be inaccurate
news_df.drop(news_df.index[[0]], inplace=True)

# drop NA values
news_df.dropna(inplace=True)

# drop any labels that aren't set properly
news_df = news_df[news_df['label'].map(len) > 0]

# drop any with headline=0
news_df = news_df[news_df['headline'] != 0]

news_df.reset_index(level=0, inplace=True)

# save to csv
news_df.to_csv('input/headlines_pn.csv', index=False)
