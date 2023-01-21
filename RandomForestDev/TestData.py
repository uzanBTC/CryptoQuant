# -*- coding: utf-8 -*-
# @Time    : 2023-01-17 8:00
# @Author  : Wu Zhenhuan
# @FileName: TestData.py
# @Software: PyCharm

import pandas as pd

from RandomForestDev.KDJ import KDJ
from RandomForestDev.MACD import MACD
from RandomForestDev.OBV import OBV
from RandomForestDev.RSI import RSI
from RandomForestDev.StockIndicators import StockIndicators
from RandomForestDev.StockRandomForest import StockRandomForest
from RandomForestDev.Williams import Williams

if __name__=="__main__":
    '''rfc=StockRandomForest("test_strategy")
    holc=pd.read_csv("../data/price_data.csv")
    indicators=StockIndicators(holc)
    rsi=indicators.rsi
    #obv=indicators.get_obv()
    print(str(indicators))'''

    ohlcv = pd.read_csv("../data/price_data.csv")

    data=ohlcv.copy()
    del data['open'],data['high'],data['low'],data['close'],data['volume']

    rsi=RSI(ohlcv=ohlcv)
    obv=OBV(ohlcv)
    macd=MACD(ohlcv)
    william=Williams(ohlcv)

    data['rsi']=rsi.indicator
    data['obv']=obv.indicator
    data['macd']=macd.dea
    data['william']=william.indicator
    data['kdj']=KDJ(ohlcv).indicator
    print(data)


