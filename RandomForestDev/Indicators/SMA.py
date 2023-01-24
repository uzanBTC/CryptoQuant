from RandomForestDev.Indicators.MarketIndicator import MarketIndicator
import pandas as pd


class SMA(MarketIndicator):
    def __init__(self, ohlcv: pd.DataFrame, term_n):
        self.term_n = term_n
        super().__init__(ohlcv)

    def calculate_indicator(self, ohlcv) -> pd.Series:
        price_data = ohlcv
        sman = price_data['close'].transform(lambda x: x.rolling(window=self.term_n).mean())
        return sman
