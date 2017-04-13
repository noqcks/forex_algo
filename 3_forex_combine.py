import pandas as pd
import numpy as np
# 1.
# python3 /usr/local/lib/python3.6/site-packages/duka/main.py USDCAD -s 2017-03-01 -e 2017-03-17

# 2. combine data into 2 hour chunks
# datetime (2 hour), Open Ask, High Ask, Low Ask, Close Ask, Open Bid, High Bid, Low Bid, Close Bid
# Close Bid one period = Open Bid next period
# Close Ask one period = Open Ask next period

def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')

df = pd.read_csv('USDCAD-2017_03_01-2017_03_17.csv', names=['datetime', 'ask', 'bid', 'askvolume', 'bidvolume'])
df.drop(['askvolume','bidvolume'], axis=1, inplace=True)
df.set_index('datetime', inplace=True)

# convert datetime to DateTimeIndex
df.index = pd.to_datetime(df.index)

# group into 2H period and add columns
# [Open Ask, High Ask, Low Ask, Close Ask, Open Bid, High Bid, Low Bid, Close Bid]
fs = dict(Open='first', Close='last', Max='max')
ag = dict(Ask=fs, Bid=fs)
gp = pd.TimeGrouper('2H')
df = df.rename(columns=str.capitalize).groupby(gp).agg(ag)
df = df.swaplevel(0, 1, 1)
df.columns = df.columns.map(' '.join)
df.reset_index(level=0, inplace=True)
df = df.dropna(how='any')


df.to_csv('USDCAD-2017_03_01-2017_03_17_grouped.csv', index=False)
