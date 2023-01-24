# -*- coding: utf-8 -*-
# @Time    : 2023-01-17 8:00
# @Author  : Wu Zhenhuan
# @FileName: TestData.py
# @Software: PyCharm

import pandas as pd

from RandomForestDev.Indicators.ATR import ATR
from RandomForestDev.Indicators.BollingBands import BollingBands
from RandomForestDev.Indicators.EMA import EMA
from RandomForestDev.Indicators.KDJ import KDJ
from RandomForestDev.Indicators.OBV import OBV
from RandomForestDev.Indicators.RSI import RSI
from RandomForestDev.Indicators.Williams import Williams

def generateTestData(path=None):
    file_path="../data/price_data.csv" if not path else path
    ohlcv=pd.read_csv(file_path)
    data = ohlcv.copy()
    del data['open'], data['high'], data['low'], data['close'], data['volume']

    '''
    Data as feature:
    1. RSI
    2. KD
    3. DIF/DEA
    4. EMA3/EMA8
    5. EMA8/EMA21
    6. ATR3/ATR21
    7. OBV/SMA(OBV,21)
    '''

    ema3=EMA(ohlcv,term_n=3)
    ema8=EMA(ohlcv,term_n=8)
    ema21=EMA(ohlcv,term_n=21)

    ema3v8=(ema3.indicator-ema8.indicator)/ema8.indicator
    ema8v21 = (ema8.indicator - ema21.indicator) / ema21.indicator

    atr3=ATR(ohlcv,term=3)
    atr21 = ATR(ohlcv, term=21)
    atr_ratio=(atr3.indicator-atr21.indicator)/atr21.indicator

    rsi = RSI(ohlcv=ohlcv)
    obv = OBV(ohlcv)
    william = Williams(ohlcv)

    data['rsi'] = rsi.indicator
    data['obv_ratio'] = (obv.indicator-obv.sma)/obv.sma
    data['william'] = william.indicator
    data['kdj'] = KDJ(ohlcv).indicator
    data['ema3v8']=ema3v8
    data['ema8v21']=ema8v21
    data['atr_ratio']=atr_ratio

    '''
    Prediction:
    Bolling
    shift
    '''
    bolling=BollingBands(ohlcv)

    closed_group=ohlcv['close']
    # 未来7天的价格能不能超过当前的布林带上轨（平均值的两个标准差）
    closed_group=closed_group.shift(-7) > bolling.up_band

    data['prediction']=closed_group*1
    data=data.dropna()
    return data


if __name__=="__main__":

    generateTestData(None)