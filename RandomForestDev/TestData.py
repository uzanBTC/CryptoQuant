# -*- coding: utf-8 -*-
# @Time    : 2023-01-17 8:00
# @Author  : Wu Zhenhuan
# @FileName: TestData.py
# @Software: PyCharm

import pandas as pd

from RandomForestDev.Indicators.ATR import ATR
from RandomForestDev.Indicators.EMA import EMA
from RandomForestDev.Indicators.KDJ import KDJ
from RandomForestDev.Indicators.OBV import OBV
from RandomForestDev.Indicators.RSI import RSI
from RandomForestDev.Indicators.Williams import Williams




def generateTestData(path:str):
    ohlcv=pd.read_csv("../data/price_data.csv")
    data = ohlcv.copy()
    del data['open'], data['high'], data['low'], data['close'], data['volume']



    '''
    Data needs to test:
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
    data['obv'] = obv.indicator
    data['william'] = william.indicator
    data['kdj'] = KDJ(ohlcv).indicator
    data['ema3v8']=ema3v8
    data['ema8v21']=ema8v21
    data['atr_ratio']=atr_ratio

    print(data.head(50))



if __name__=="__main__":
    '''rfc=StockRandomForest("test_strategy")
    holc=pd.read_csv("../data/price_data.csv")
    indicators=StockIndicators(holc)
    rsi=indicators.rsi
    #obv=indicators.get_obv()
    print(str(indicators))'''

    '''ohlcv = pd.read_csv("../data/price_data.csv")

    data=ohlcv.copy()
    del data['open'],data['high'],data['low'],data['close'],data['volume']

    rsi=RSI(ohlcv=ohlcv)
    obv=OBV(ohlcv)
    macd=MACD(ohlcv)
    william=Williams(ohlcv)
    atr3=ATR(ohlcv,3)
    atr21 = ATR(ohlcv, 21)

    data['rsi']=rsi.indicator
    data['obv']=obv.indicator
    data['macd']=macd.dea
    data['william']=william.indicator
    data['kdj']=KDJ(ohlcv).indicator
    data['atr']=(atr3.indicator-atr21.indicator)/atr21.indicator'''
    generateTestData(None)