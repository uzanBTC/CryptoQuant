from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader as bt
import matplotlib
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
from pylab import mpl
import datetime as dt

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

class ATRVegasStrategy(bt.Strategy):
    # 默认参数
    params = (
        ('atr_long_period',21),
        ('atr_short_period', 3),
        ('atr_ratio', 1.382),
        ('printlog', False),
        ('close_when_stop',True),
    )

    def __init__(self):
        self.big_int=10000000000


        self.buyprice = 0
        self.sellprice=self.big_int
        self.buycomm = 0
        self.atr_ratio = self.p.atr_ratio
        self.high_after_buy=0
        self.low_after_sell=self.big_int
        # -1: 空单持有  0：无持仓   1：多单持有
        self.order=0

        # 每bar真实波动率
        self.TR = bt.indicators.Max((self.data.high(0) - self.data.low(0)),
                                    abs(self.data.close(-1) - self.data.high(0)),
                                    abs(self.data.close(-1) - self.data.low(0)))

        # 平均真实波动率
        self.atr_long_term = bt.indicators.MovingAverageSimple(self.TR, period=self.p.atr_long_period)
        self.atr_short_term = bt.indicators.MovingAverageSimple(self.TR, period=self.p.atr_short_period)

        # Vegas Tunnel
        self.vegas_quick = bt.indicators.ExponentialMovingAverage(self.data.close, period=144)
        self.vegas_slow = bt.indicators.ExponentialMovingAverage(self.data.close, period=169)

        self.vegas_long_cond = bt.ind.And(self.data.close > self.vegas_quick, self.vegas_quick > self.vegas_slow)
        self.vegas_short_cond= bt.ind.And(self.data.close < self.vegas_quick, self.vegas_quick < self.vegas_slow)

        # 向上突破还是向下突破
        self.isUp = self.data.close(0) > self.data.close(-1)
        self.isDown = self.data.close(0) < self.data.close(-1)

        # atr 突破
        self.atr_signal = bt.ind.CrossOver(self.atr_short_term,self.atr_long_term*self.atr_ratio)

        # chandelier stop loss

    # 一個iterator，不斷地去迭代指向一格一格的時間
    def next(self):
        if self.order==0:
            # 没有仓位的时候发现买入信号，买入
            if self.isUp[0]==True and self.vegas_long_cond[0]==True and self.atr_signal>0:  # and self.chan_signal_long > 0:  # self.atr_signal(0)==True and  (not self.position) and
                self.buy()
                self.buyprice=self.data.close[0]
                self.high_after_buy=self.data.close[0]
                self.order=1
            # 空单条件
            elif self.isDown[0]==False and self.vegas_short_cond[0]==True and self.atr_signal>0:
                self.sell()
                self.sellprice=self.data.close[0]
                self.low_after_sell=self.data.close[0]
                self.order=-1
        # 多头持仓
        elif self.order==1:
            # 多头移动止损： 价格跌破吊灯下轨且持仓时
            if self.data.close < self.high_after_buy-3*self.atr_long_term and self.position:
                self.close()
                self.buyprice =0
                self.high_after_buy=0
                self.order = 0
            # 多头固定止损： 价格跌破买入价的2个ATR且持仓时
            elif self.data.close < (self.buyprice - 3 * self.atr_long_term) and self.position:
                self.close()
                self.buyprice =0
                self.high_after_buy=0
                self.order = 0
            else:
                self.high_after_buy=max(self.high_after_buy,self.data.close[0])
        # 空头持仓
        else:
            # 空头移动止损： 价格涨破吊灯下轨且持仓时
            if self.data.close > self.low_after_sell + 3 * self.atr_long_term and self.position:
                self.close()
                self.sellprice = self.big_int
                self.low_after_sell = self.big_int
                self.order = 0
            # 空头固定止损： 价格跌破买入价的3个ATR且持仓时
            elif self.data.close > (self.sellprice + 3 * self.atr_long_term) and self.position:
                self.close()
                self.sellprice = self.big_int
                self.low_after_sell = self.big_int
                self.order = 0
            else:
                self.low_after_sell = min(self.low_after_sell, self.data.close[0])

    # 交易记录日志（默认不打印结果）
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:\n价格:{order.executed.price},\
                成本:{order.executed.value},\
                手续费:{order.executed.comm}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:\n价格：{order.executed.price},\
                成本: {order.executed.value},\
                手续费{order.executed.comm}')

            self.bar_executed = len(self)

            # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')

    # 记录交易收益情况（默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'(组合线: {self.p.atr_long_period},{self.p.atr_short_period}); '
                 f'期末总资金: {self.broker.getvalue():.2f}', doprint=False)

    def stop(self):
        self.log(f'(组合线：{self.p.atr_long_period},{self.p.atr_short_period})；期末总资金: {self.broker.getvalue():.2f}', doprint=True)


# 由于交易过程中需要对仓位进行动态调整，每次交易一单元股票（不是固定的一股或100股，根据ATR而定），因此交易头寸需要重新设定
class TradeSizer(bt.Sizer):
    params = (
            ('stake', 1),

            )

    def _getsizing(self, comminfo, cash, data, isbuy):
        # isbuy==True，买场景，这时候需要传入用ATR计算的头寸
        if isbuy:
            return self.p.stake
        # isbuy==False，卖场景，这个时候需要的是现有的持仓头寸，用于去卖
        position = self.broker.getposition(data)
        if not position.size:
            return 0
        else:
            return position.size


def convert_csv_to_dataframe(csv_path):
    dataframe = pd.read_csv(csv_path)
    dataframe['time'] = pd.to_datetime(dataframe['time'])
    dataframe.set_index('time', inplace=True)
    return dataframe


def run_BTC_optimize(long_list, short_list, data_path, startcash=10000000, com=0.0005):

    cerebro = bt.Cerebro()
    # 导入策略参数寻优
    cerebro.optstrategy(ATRVegasStrategy, atr_long_period=long_list, atr_short_period=short_list)
    #cerebro.addstrategy(ATRVegasStrategy)

    df = convert_csv_to_dataframe(data_path)

    data = bt.feeds.PandasData(dataname=df, fromdate=dt.datetime(2019, 8, 17),
                                    todate=dt.datetime(2022,12, 24), timeframe=bt.TimeFrame.Days)

    cerebro.adddata(data)
    # broker设置资金、手续费
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission=com)
    # 设置买入设置，策略，数量
    #cerebro.addsizer(TradeSizer)
    cerebro.addsizer(bt.sizers.PercentSizer,percents=90)
    print('期初总资金: %.2f' % cerebro.broker.getvalue())

    cerebro.run()


def run_single_plot(data_path, printlog=True ,startcash=10000000, com=0.0005):

    cerebro = bt.Cerebro()
    # 导入策略参数寻优
    #cerebro.optstrategy(ATRVegasStrategy, atr_long_period=long_list, atr_short_period=short_list)
    cerebro.addstrategy(ATRVegasStrategy, printlog=printlog)

    df = convert_csv_to_dataframe(data_path)

    data = bt.feeds.PandasData(dataname=df, fromdate=dt.datetime(2019, 8, 17),
                                    todate=dt.datetime(2022,12, 24), timeframe=bt.TimeFrame.Days)

    cerebro.adddata(data)
    # broker设置资金、手续费
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission=com)
    # 设置买入设置，策略，数量
    #cerebro.addsizer(TradeSizer)
    cerebro.addsizer(bt.sizers.PercentSizer,percents=90)
    print('期初总资金: %.2f' % cerebro.broker.getvalue())

    # Add pyfolio as analyzer
    # cerebro.addanalyzer(bt.analyzers.PyFolio)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')

    result = cerebro.run()

    print('夏普比率: ', result[0].analyzers.SharpeRatio.get_analysis()['sharperatio'])
    print('最大回撤: ', result[0].analyzers.DrawDown.get_analysis()['max']['drawdown'], "%")

    cerebro.plot()


def run_single_plot_4h(data_path, printlog=True ,startcash=10000000, com=0.0005):

    cerebro = bt.Cerebro()
    # 导入策略参数寻优
    #cerebro.optstrategy(ATRVegasStrategy, atr_long_period=long_list, atr_short_period=short_list)
    cerebro.addstrategy(ATRVegasStrategy, printlog=printlog)

    df = convert_csv_to_dataframe(data_path)

#2021-05-21 12:00:00
    #2022-12-26 20:00:00
    data = bt.feeds.PandasData(dataname=df, fromdate=dt.datetime(2021, 5, 21,12,0,0),
                                    todate=dt.datetime(2022,12, 26,20,0,0), timeframe=bt.TimeFrame.Minutes)

    cerebro.adddata(data)
    # broker设置资金、手续费
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission=com)
    # 设置买入设置，策略，数量
    #cerebro.addsizer(TradeSizer)
    cerebro.addsizer(bt.sizers.PercentSizer,percents=90)
    print('期初总资金: %.2f' % cerebro.broker.getvalue())

    # Add pyfolio as analyzer
    # cerebro.addanalyzer(bt.analyzers.PyFolio)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')

    result = cerebro.run()

    print('夏普比率: ', result[0].analyzers.SharpeRatio.get_analysis()['sharperatio'])
    print('最大回撤: ', result[0].analyzers.DrawDown.get_analysis()['max']['drawdown'], "%")

    cerebro.plot()


def run_optimize_4h(long_list, short_list, data_path, startcash=10000000, com=0.0005):

    cerebro = bt.Cerebro()
    # 导入策略参数寻优
    cerebro.optstrategy(ATRVegasStrategy, atr_long_period=long_list, atr_short_period=short_list)
    #cerebro.addstrategy(ATRVegasStrategy)

    df = convert_csv_to_dataframe(data_path)

    data = bt.feeds.PandasData(dataname=df, fromdate=dt.datetime(2021, 5, 21, 12, 0, 0),
                               todate=dt.datetime(2022, 12, 26, 20, 0, 0), timeframe=bt.TimeFrame.Minutes)

    cerebro.adddata(data)
    # broker设置资金、手续费
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission=com)
    # 设置买入设置，策略，数量
    #cerebro.addsizer(TradeSizer)
    cerebro.addsizer(bt.sizers.PercentSizer,percents=90)
    print('期初总资金: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

if __name__ == "__main__":
    #run_BTC_optimize(long_list=[7,14,21,28,35,42,49,56,63,72,81],short_list=range(1,7))
    #run_single_plot("../data/eth_backtesting.csv")
    #run_single_plot_4h("../data/eth_backtesting_4h.csv")
    run_optimize_4h(long_list=[7,14,21,28,35,42,49,56,63,72,81],short_list=range(1,7),data_path="../data/eth_backtesting_4h.csv")
