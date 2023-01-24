from typing import Tuple

from RandomForestDev.Indicators.MarketIndicator import MarketIndicator
import pandas as pd

class MACD(MarketIndicator):
    def __init__(self, ohlcv: pd.DataFrame,fast_n=12,slow_n=26,dea_n=9):
        self._dif = None
        self._dea = None
        self._fast_n=fast_n
        self._slow_n=slow_n
        self._dea_n=dea_n
        super().__init__(ohlcv)

    def calculate_indicator(self, ohlcv) -> Tuple[pd.Series,pd.Series]:
        price_data = ohlcv
        ema_slow = price_data['close'].transform(lambda x: x.ewm(span=self._slow_n).mean())
        ema_fast = price_data['close'].transform(lambda x: x.ewm(span=self._fast_n).mean())
        macd = ema_fast - ema_slow

        # Calculate the EMA
        ema_n_macd = macd.ewm(span=self._dea_n).mean()

        # Store the data in the data frame.
        price_data['MACD'] = macd
        price_data['MACD_EMA'] = ema_n_macd
        self._dif=macd
        self._dea=ema_n_macd
        return price_data['MACD'], price_data['MACD_EMA']


    @property
    def dif(self):
        return self._dif

    @property
    def dea(self):
        return self._dea