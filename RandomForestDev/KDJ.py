
import pandas as pd

from RandomForestDev.MarketIndicator import MarketIndicator


class KDJ(MarketIndicator):

    def __init__(self, ohlcv: pd.DataFrame ,n=14):
        self.n =n
        super().__init__(ohlcv)

    def calculate_indicator(self, ohlcv) -> pd.Series:
        price_data = ohlcv
        low_14, high_14 = price_data[['low']].copy(), price_data[['high']].copy()

        # Group by symbol, then apply the rolling function and grab the Min and Max.
        low_14 = low_14['low'].transform(lambda x: x.rolling(window=self.n).min())
        high_14 = high_14['high'].transform(lambda x: x.rolling(window=self.n).max())

        # Calculate the Stochastic Oscillator.
        k_percent = 100 * ((price_data['close'] - low_14) / (high_14 - low_14))

        # Add the info to the data frame.
        price_data['low_14'] = low_14
        price_data['high_14'] = high_14
        price_data['k_percent'] = k_percent
        return price_data['k_percent']


