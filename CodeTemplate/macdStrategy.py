from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
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
         self.data0.close, **kwargs
        )

        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.macdsignal, plot=False)

        self.bug_signal = (self.crossover==1)
        self.sell_signal = (self.crossover==-1)
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
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2018, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2020, 12, 31),
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
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

