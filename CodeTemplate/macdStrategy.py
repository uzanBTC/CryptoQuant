from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds
import talib


'''
MACD: (12-day EMA - 26-day EMA) 

Signal Line: 9-day EMA of MACD

MACD Histogram: MACD - Signal Line
'''

# Create a Stratey
class MACDStrategy(bt.Strategy):
    params = (
        ('fastperiod', 10),
        ('slowperiod',22),
        ("signalperiod", 8),
    )

    def __init__(self):
        kwargs = {
           "fastperiod": self.p.fastperiod,
           "fastmatype": bt.talib.MA_Type.EMA,
           "slowperiod": self.p.slowperiod,
           "slowmatype": bt.talib.MA_Type.EMA,
           "signalperiod": self.p.signalperiod,
           "signalmatype": bt.talib.MA_Type.EMA
        }
        self.macd = bt.talib.MACDEXT(
         self.datas[0].close, **kwargs
        )

        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.macdsignal, plot=False)

        # backtrader构造逻辑运算的方式
        # 两线都在零轴上方金叉
        self.above = bt.And(self.macd.macd>0.0, self.macd.macdsignal>0.0)

        self.bug_signal = bt.And(self.above,self.crossover==1)
        self.sell_signal = (self.crossover==-1)

        #self.bug_signal = (self.crossover == 1)
        #self.sell_signal = (self.crossover == -1)
        # To keep track of Pending orders
        self.order=None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            self.order = None

    def next(self):
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            if self.bug_signal:
                self.order = self.buy()
        else:
            if self.sell_signal:
                self.order = self.sell()

class MyHLOC(btfeeds.GenericCSVData):

#datetime: year, month=None, day=None, hour=0, minute=0, second=0,
#2022-12-01 14:40:00
#2022-12-07 12:15:00
#time,open,high,low,close,volume
  params = (
    ('fromdate', datetime.datetime(2022,12,1,14,40,0)),
    ('todate', datetime.datetime(2022,12,7,12,15,0)),
    ('nullvalue', 0.0),
    ('dtformat', ('%Y-%m-%d %H:%M:%S')),
    ('tmformat', ('%Y-%m-%d %H:%M:%S')),
    ('timeframe',bt.TimeFrame.Minutes),
    ('compression', 5),
    ('datetime', 0),
    ('time', -1),
    ('open', 1),
    ('high', 2),
    ('low', 3),
    ('close', 4),
    ('volume', 5),
    ('openinterest', -1),
)

def yahooData():
    return bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2018, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2021, 8, 6),
        # Do not pass values after this date
        reverse=False,
        timeframe=bt.TimeFrame.Days
        )

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    # to optimize the period of the Simple Moving Average instead of passing a value a range of values is passed
    strats = cerebro.addstrategy(
        MACDStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../data/TSLA.csv')

    # Create a Data Feed
    # Parses pre-downloaded Yahoo CSV Data Feeds (or locally generated if they comply to the Yahoo format
    dataTSL = yahooData()

    # Add the Data Feed to Cerebro

    data = MyHLOC(dataname='../data/backtesting.csv')

    cerebro.adddata(dataTSL, name="TSLA")
    cerebro.adddata(data, name="BTC")
    #cerebro.resampledata(data, name="5m", timeframe=bt.TimeFrame.Minutes,compression=5)
    #cerebro.resampledata(data, name="15m",timeframe=bt.TimeFrame.Minutes,compression=15)

    cerebro.broker.setcash(10000.0)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0005)

    # 以发出信号的收盘价成交
    cerebro.broker.set_coc(True)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.AllInSizerInt,percents=99)

    cerebro.addanalyzer(bt.analyzers.AnnualReturn)
    cerebro.addanalyzer(bt.analyzers.TimeDrawDown)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    cerebro.addanalyzer(bt.analyzers.SQN)

    # Run over everything
    result=cerebro.run()

    ana = result[0].analyzers.sqn.get_analysis()
    # sqn指数：交易次数乘以类夏普率
    # sharpe ratio: 目的是计算投资组合每承受一单位总风险，会产生多少的超额报酬
    print("sqn: {:.3f}, trades:{:d}".format(ana['sqn'],ana['trades']))

    cerebro.plot()

