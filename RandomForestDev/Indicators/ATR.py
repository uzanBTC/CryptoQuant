from RandomForestDev.Indicators.MarketIndicator import MarketIndicator
import pandas as pd
import numpy as np

class ATR(MarketIndicator):
    def __init__(self, ohlcv: pd.DataFrame,term=21):
        self.term=term
        super().__init__(ohlcv)

    def calculate_indicator(self, ohlcv) -> pd.Series:
        high_low=ohlcv['high']-ohlcv['low']
        high_close=np.abs(ohlcv['high']-ohlcv['close'])
        low_close=np.abs(ohlcv['low']-ohlcv['close'])
        ranges=pd.concat([high_low,high_close,low_close],axis=1)
        true_range=np.max(ranges,axis=1)
        atr=true_range.rolling(self.term).sum()/self.term
        return atr
