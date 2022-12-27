import datetime
import backtrader.feeds as btfeeds
import pandas as pd

'''
data = btfeeds.GenericCSVData(
    dataname='../data/BINANCE_ETHUSDT5m.csv',

    fromdate=datetime.datetime(2000, 1, 1),
    todate=datetime.datetime(2000, 12, 31),

    nullvalue=0.0,

    dtformat=('%Y-%m-%d'),

    datetime=0,
    high=1,
    low=2,
    open=3,
    close=4,
    volume=5,
    openinterest=-1
)


datetime (default: 0) column containing the date (or datetime) field

time (default: -1) column containing the time field if separate from the datetime field (-1 indicates it’s not present)

open (default: 1) , high (default: 2), low (default: 3), close (default: 4), volume (default: 5), openinterest (default: 6)

Index of the columns containing the corresponding fields

If a negative value is passed (example: -1) it indicates the field is not present in the CSV data

nullvalue (default: float(‘NaN’))

Value that will be used if a value which should be there is missing (the CSV field is empty)

dtformat (default: %Y-%m-%d %H:%M:%S)

Format used to parse the datetime CSV field

tmformat (default: %H:%M:%S)

Format used to parse the time CSV field if “present” (the default for the “time” CSV field is not to be present)
'''

class MyHLOC(btfeeds.GenericCSVData):

#2017-08-17 08:00:00
  params = (
    ('fromdate', datetime.datetime(2017,8,17)),
    ('todate', datetime.datetime(2022,12,25)),
    ('nullvalue', 0.0),
    ('dtformat', '%Y-%m-%d'),
    ('tmformat', '%Y-%m-%d'),
    ('datetime', 0),
    ('time', 1),
    ('high', 2),
    ('low', 3),
    ('open', 4),
    ('close', 5),
    ('volume', 6),
    ('openinterest', -1)
)

def dateTimeConvertor(s):
  ss = datetime.datetime.fromtimestamp(s)
  return ss

def csvTimeUnixToDatetime(csv_path,to_file_path, time_column):
  df = pd.read_csv(csv_path)
  dt_list=[]
  for index, row in df.iterrows():
    dt_list.append(dateTimeConvertor(row[time_column]))

  df[time_column]=dt_list
  #df.to_csv("data/backtesting.csv", index=False)
  df.to_csv(to_file_path,index=False)
  print(df[time_column])


if __name__=="__main__":
    #data = MyHLOC(dataname='../data/backtesting.csv')
    #print(data.params)
    #print(dateTimeConvertor(1669876800))
    #csvTimeUnixToDatetime("data/BINANCE_ETHUSDTPERP, 1D.csv","data/eth_backtesting.csv","time")
    csvTimeUnixToDatetime("data/BINANCE_ETHUSDTPERP, 240.csv", "data/eth_backtesting_4h.csv", "time")


