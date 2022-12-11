import backtrader as bt
import pandas as pd
import datetime as dt
import numpy as np


class SMAStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.data0.close
        self.order = None
        self.buyprice= None
        self.buycomm=None

        self.sma=bt.indicators.MovingAverageSimple(self.data0,period=15)

    def next(self):
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                # balance
                self.close()



if __name__=='__main__':
    cerebro=bt.Cerebro()
    dataframe=pd.read_csv('../data/TSLA.csv')
    dataframe['Datetime'] = pd.to_datetime(dataframe['Date'])
    dataframe.set_index('Datetime',inplace=True)
    data_TSLA = bt.feeds.PandasData(dataname=dataframe, fromdate=dt.datetime(2018,1,1),todate=dt.datetime(2021,6,1),timeframe=bt.TimeFrame.Minutes)
    cerebro.adddata(data_TSLA)

    cerebro.addstrategy(SMAStrategy)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio,_name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')

    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.0006)

    cerebro.addsizer(bt.sizers.PercentSizer,percents=90)
    result = cerebro.run()

    print('夏普比率: ', result[0].analyzers.SharpeRatio.get_analysis()['sharperatio'])
    print('最大回撤: ', result[0].analyzers.DrawDown.get_analysis()['max']['drawdown'],"%")

    cerebro.plot()