import pandas as pd
import glob

# 1.
path = '/Users/noqcks/data/data_science/algo_trading/news' # use your path

allFiles = glob.glob(path + "/*.csv")

frame = pd.DataFrame()

list_ = []

for file_ in allFiles:
    df = pd.read_csv(file_,index_col=None, header=0)
    list_.append(df)

frame = pd.concat(list_, ignore_index=True)
frame.drop_duplicates(keep='first', inplace=True)

frame.to_csv('news/MarketWatch-Combined.csv', index=False)

# 2. combine news into 2 hour chunks
