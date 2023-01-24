from RandomForestDev.Indicators.MarketIndicator import MarketIndicator

import pandas as pd

class OBV(MarketIndicator):
    def __init__(self, ohlcv: pd.DataFrame,term=21):
        self.term=term
        super().__init__(ohlcv)
        self._obv_sma=self.obv_sma()

    def calculate_indicator(self, ohlcv) -> pd.Series:
        price_data = ohlcv
        change = price_data['close'].diff()
        volume = price_data['volume']

        # intialize the previous OBV
        prev_obv = 0
        obv_values = []

        # calculate the On Balance Volume
        for i, j in zip(change, volume):

            if i > 0:
                current_obv = prev_obv + j
            elif i < 0:
                current_obv = prev_obv - j
            else:
                current_obv = prev_obv

            # OBV.append(current_OBV)
            prev_obv = current_obv
            obv_values.append(current_obv)

        # Return a panda series.
        return pd.Series(obv_values, index=price_data.index)

    def obv_sma(self):
        return self.indicator.rolling(window=self.term).mean()


    @property
    def sma(self):
        return self._obv_sma


 