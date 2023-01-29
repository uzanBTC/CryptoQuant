from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader as bt
from pylab import mpl
import datetime as dt
import numpy as np

import warnings

from StrategyDev.FinanceAnalyzers.CerebroAnalyzers import add_analyzers_to_bt_cerebro, cerebro_result_visualizer
from StrategyDev.Indicators.OnBalanceVolume import OnBalanceVolume
from StrategyDev.utils import model_load, convert_csv_to_dataframe

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

class RFStrategy(bt.Strategy):
    # 默认参数
    params = (
        ('model',None),
        ('printlog', False),
    )

    def __init__(self):
        '''
        col_list=['rsi','obv_ratio','william','ema3v8','ema8v21','atr_ratio']
            Data as feature:
            1. RSI
            2. EMA3/EMA8
            3. EMA8/EMA21
            4. ATR3/ATR21
            5. OBV/SMA(OBV,21)
        '''
        self.model=self.p.model


        self.ema3=bt.indicators.ExponentialMovingAverage(self.data.close, period=3)
        self.ema8 = bt.indicators.ExponentialMovingAverage(self.data.close, period=8)
        self.ema21 = bt.indicators.ExponentialMovingAverage(self.data.close, period=21)

        # 每bar真实波动率
        self.TR = bt.indicators.Max((self.data.high(0) - self.data.low(0)),
                                    abs(self.data.close(-1) - self.data.high(0)),
                                    abs(self.data.close(-1) - self.data.low(0)))

        # 平均真实波动率
        self.atr_short_term = bt.indicators.MovingAverageSimple(self.TR, period=3)
        self.atr_long_term = bt.indicators.MovingAverageSimple(self.TR, period=21)
        self.obv=OnBalanceVolume(self.data)
        self.obv_sma=bt.indicators.MovingAverageSimple(self.obv,period=21)

        self.rsi=bt.indicators.RSI_EMA(self.data.close,period=14)
        self.obv_ratio=(self.obv-self.obv_sma)/self.obv_sma  # (obv.indicator-obv.sma)/obv.sma
        self.william=bt.indicators.WilliamsR()
        self.ema3v8=(self.ema3-self.ema8)/self.ema8
        self.ema8v21=(self.ema8-self.ema21)/self.ema21
        self.atr_ratio=(self.atr_short_term-self.atr_long_term)/self.atr_long_term

        self.vegas_quick = bt.indicators.ExponentialMovingAverage(self.data.close, period=144)
        self.vegas_slow = bt.indicators.ExponentialMovingAverage(self.data.close, period=169)

        self.vegas_long_cond = bt.ind.And(self.data.close > self.vegas_quick, self.vegas_quick > self.vegas_slow)
        self.vegas_short_cond = bt.ind.And(self.data.close < self.vegas_quick, self.vegas_quick < self.vegas_slow)

        '''
        stop loss
        '''
        self.order=0
        self.high_after_buy=0


    # 一個iterator，不斷地去迭代指向一格一格的時間
    def next(self):
        if self.order==0:
            # 没有仓位的时候发现买入信号，买入
            signal_ml = self.model_predict()
            if signal_ml ==1 and self.vegas_long_cond[0]:
                self.buy()
                self.buyprice = self.data.close[0]
                self.high_after_buy = self.data.close[0]
                self.order=1
        # 多头持仓
        elif self.order==1:
            # 多头移动止损： 价格跌破吊灯下轨且持仓时
            # 跌破3倍ATR
            stop_loss_cond_one=self.data.close < self.high_after_buy-3*self.atr_long_term
            # 跌破2倍ATR且同时跌破中期均线
            stop_loss_cond_two=self.data.close < self.high_after_buy-2*self.atr_long_term and self.data.close < self.ema21
            if self.position and (stop_loss_cond_one or stop_loss_cond_two):
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
            # 没有触发止损，更新吊灯止损参考值
            else:
                self.high_after_buy=max(self.high_after_buy,self.data.close[0])

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
        self.log(f'期末总资金: {self.broker.getvalue():.2f}', doprint=False)

    def stop(self):
        self.log(f'期末总资金: {self.broker.getvalue():.2f}', doprint=True)


    def model_predict(self):
        warnings.simplefilter("ignore", UserWarning)
        input_data = np.array([self.rsi[0], self.obv_ratio[0], self.william[0], self.ema3v8[0], self.ema8v21[0],
                               self.atr_ratio[0]]).reshape(1, -1)
        return self.model.predict(input_data)[0]


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


