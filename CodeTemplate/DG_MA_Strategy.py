import datetime

import backtrader as bt
import pandas as pd
import datetime as dt
import numpy as np
import backtrader.feeds as btfeeds


'''
开仓：以多头为例五分钟级别ma3>ma10>ma20>ma40或ma3>ma10>ma20>ma40>ma60
      同时需满足一下任一条件中的任意一个：
1.	币价突破ma3时满足成交量放大，暂定为此成交量大于上一根50%；
2.	一分钟级别k线满足ma5>ma10>ma20
平仓：五分钟级别k线ma3跌破ma7
'''

'''
Long:
  if sma3>sma10>sma20>sma40 and (price>sma3 and volume[0] > 1.5* volume[-1]):
    buy()
  if sma3<sma5:
    balance()
'''

class SMAStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.data0.close
        self.order = None
        self.buyprice= None
        self.buycomm=None

        self.sma3=bt.indicators.MovingAverageSimple(self.datas[0],period=3)
        self.sma5=bt.indicators.MovingAverageSimple(self.datas[0],period=5)
        self.sma10 = bt.indicators.MovingAverageSimple(self.datas[0], period=10)
        self.sma20 = bt.indicators.MovingAverageSimple(self.datas[0], period=20)
        self.sma40 = bt.indicators.MovingAverageSimple(self.datas[0], period=40)
        self.volumeNow=self.data.volume(0)
        self.volumePrev=self.data.volume(-1)

    '''
    Long:
      if sma3>sma10>sma20>sma40 and (price>sma3 and volume[0] > 1.5* volume[-1]):
        buy()
      if sma3<sma5:
        balance()
    '''

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.time(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

            # Check if an order has been completed
            # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

            # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        if not self.position:
            if (self.dataclose>self.sma3>self.sma10>self.sma20>self.sma40) and (self.volumeNow >= 2 * self.volumePrev):
                self.buy()
        else:
            if self.sma3<self.sma5:
                # balance
                self.sell()

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
    ('datetime', 0),
    ('time', -1),
    ('open', 1),
    ('high', 2),
    ('low', 3),
    ('close', 4),
    ('volume', 5),
    ('openinterest', -1),
)


if __name__=='__main__':
    #validate("2022-12-01 14:40:00")
    cerebro=bt.Cerebro()

    data= MyHLOC(dataname='../data/backtesting.csv')
    cerebro.broker.setcash(1000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=0.5)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    #cerebro.adddata(data)
    cerebro.resampledata(data,timeframe=bt.TimeFrame.Minutes,compression=5)
    cerebro.addstrategy(SMAStrategy)

    cerebro.run()
    cerebro.plot()
