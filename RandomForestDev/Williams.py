from RandomForestDev.MarketIndicator import MarketIndicator
import pandas as pd

class Williams(MarketIndicator):

    def __init__(self, ohlcv: pd.DataFrame,n=14):
        self.n = n
        super().__init__(ohlcv)


    def calculate_indicator(self, ohlcv) -> pd.Series:
        price_data = ohlcv
        # Make a copy of the high and low column.
        low_14, high_14 = price_data[['low']].copy(), price_data[['high']].copy()

        # Group by symbol, then apply the rolling function and grab the Min and Max.
        low_14 = low_14['low'].transform(lambda x: x.rolling(window=self.n).min())
        high_14 = high_14['high'].transform(lambda x: x.rolling(window=self.n).max())

        # Calculate William %R indicator.
        r_percent = ((high_14 - price_data['close']) / (high_14 - low_14)) * - 100

        # Add the info to the data frame.
        price_data['r_percent'] = r_percent
        return price_data['r_percent']
