from RandomForestDev.Indicators.MarketIndicator import MarketIndicator

import pandas as pd

class BollingBands(MarketIndicator):
    def __init__(self, ohlcv: pd.DataFrame,term=21):
        self.term=term
        self._up_band=None
        self._low_band=None
        super().__init__(ohlcv)

    def calculate_indicator(self, ohlcv):
        data=ohlcv
        data['typical']=(data['close']+data['high']+data['low'])/3
        data['std']=data['typical'].rolling(self.term).std(ddof=0)
        data['ma-typical']=data['typical'].rolling(self.term).mean()
        self._up_band=data['ma-typical']+2*data['std']
        self._low_band=data['ma-typical'] - 2 * data['std']
        data['up']=self._up_band
        data['low'] =self._low_band
        return data['up'],data['low']

    @property
    def up_band(self):
        return self._up_band

    @property
    def low_band(self):
        return self._low_band




