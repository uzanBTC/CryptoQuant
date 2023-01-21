from RandomForestDev.MarketIndicator import MarketIndicator

import pandas as pd

class OBV(MarketIndicator):
    def __init__(self, ohlcv: pd.DataFrame):
        super().__init__(ohlcv)

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

 