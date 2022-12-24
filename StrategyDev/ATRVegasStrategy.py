from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader as bt
import matplotlib
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
from pylab import mpl

from Indicators.ChandelierExit import ChandelierExit

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


class ATRVegasStrategy(bt.Strategy):
    # 默认参数
    params = (
        ('atr_long_period', 20),
        ('atr_short_period', 10),
        ('chan_period', 4),
        ('stop_loss_multip',3),
        ('printlog', False),
    )

    def __init__(self):
        self.order = None
        self.buyprice = 0
        self.buycomm = 0
        self.buy_size = 0
        self.bar_count_after_buy = 0

        # channel for trend indicating
        # for long
        self.H_line = bt.indicators.Highest(self.data.close(-1), period=self.p.chan_period)
        # for short
        self.L_line = bt.indicators.Lowest(self.data.close(-1), period=self.p.chan_period)

        # 每bar真实波动率
        self.TR = bt.indicators.Max((self.data.high(0) - self.data.low(0)),
                                    abs(self.data.close(-1) - self.data.high(0)),
                                    abs(self.data.close(-1) - self.data.low(0)))

        # 平均真实波动率
        self.atr_long_term = bt.indicators.MovingAverageSimple(self.TR, period=self.p.atr_long_period)
        self.atr_short_term = bt.indicators.MovingAverageSimple(self.TR, period=self.p.atr_short_period)

        # Vegas Tunnel
        self.vegas_short = bt.indicators.ExponentialMovingAverage(self.data.close,period=144)
        self.vegas_long = bt.indicators.ExponentialMovingAverage(self.data.close,period=169)

        # 轨道突破
        self.chan_signal_long = bt.ind.CrossUp(self.close(0), self.H_line)
        self.chan_signal_short = bt.ind.CrossDown(self.data.close(0), self.L_line)

        # atr 突破
        self.atr_signal = (self.atr_short_term / self.atr_long_term) >= self.atr_ratio

        self.long_signal = bt.ind.And(self.chan_signal_long > 0, self.atr_signal)
        self.short_signal = bt.ind.And(self.chan_signal_short > 0, self.atr_signal)


        # chandelier stop loss
        self.stop_loss = ChandelierExit(self.data,period=22,multip=3)


    # 一個iterator，不斷地去迭代指向一格一格的時間
    def next(self):
        if self.order:
            return
        # 没有仓位的时候发现买入信号，买入
        if not self.position and self.long_signal:
            self.sizer.p.stake = 90
            self.order = self.buy()
        # 多头移动止损： 价格跌破吊灯下轨且持仓时
        elif self.data.close < self.stop_loss.long and self.position > 0:
            self.order = self.close()
        # 多头固定止损： 价格跌破买入价的2个ATR且持仓时
        elif self.data.close < (self.buyprice - 2 * self.atr_long_term) and self.position > 0:
            self.order = self.sell()
            self.buy_count = 0

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
        self.order = None

    # 记录交易收益情况（默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'(组合线: {self.p.long_period},{self.p.short_period}); '
                 f'期末总资金: {self.broker.getvalue():.2f}', doprint=False)

    def stop(self):
        self.log(f'(组合线：{self.p.long_period},{self.p.short_period})；期末总资金: {self.broker.getvalue():.2f}', doprint=True)


# 由于交易过程中需要对仓位进行动态调整，每次交易一单元股票（不是固定的一股或100股，根据ATR而定），因此交易头寸需要重新设定
class TradeSizer(bt.Sizer):
    params = (('stake', 1),)

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
