import pandas as pd
import numpy as np
import subprocess

# config
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
s_date = config['DEFAULT']['start_date']
e_date = config['DEFAULT']['end_date']
currency_pair = config['DEFAULT']['currency_pair']
file_name = "{0}-{1}-{2}".format(currency_pair, s_date.replace("-", "_"), e_date.replace("-", "_"))


############################
### 2. GET FOREX DATA  #####
############################

##
# We will grab FOREX ticker data for a currency pair from dukascopy and
# combine into 2H intervals
##

print("Getting forex data...")

# get forex ticker data from dukascopy
subprocess.call("./download_forex_data.sh {0} {1} {2}".format(currency_pair, s_date, e_date), shell=True)

print("Transforming forex data...")

# read forex ticker data csv
forex_df = pd.read_csv('input/{0}.csv'.format(file_name))
forex_df.columns = ['datetime', 'ask', 'bid', 'askvolume', 'bidvolume']

#drop volume
forex_df.drop(['askvolume','bidvolume'], axis=1, inplace=True)

# set datetime as index
forex_df.set_index('datetime', inplace=True)

# convert datetime to DateTimeIndex
forex_df.index = pd.to_datetime(forex_df.index)

# group into 2H period and add columns
# [Open Ask, High Ask, Low Ask, Close Ask, Open Bid, High Bid, Low Bid, Close Bid]
fs = dict(Open='first', Close='last', Max='max')
ag = dict(Ask=fs, Bid=fs)
gp = pd.TimeGrouper('2H')
forex_df = forex_df.rename(columns=str.capitalize).groupby(gp).agg(ag)
forex_df = forex_df.swaplevel(0, 1, 1)
forex_df.columns = forex_df.columns.map(' '.join)
forex_df.reset_index(level=0, inplace=True)
forex_df = forex_df.dropna(how='any')

forex_df.to_csv('input/{0}_grouped.csv'.format(file_name), index=False)

print("Finished.")
