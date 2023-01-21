from RandomForestDev.MarketIndicator import MarketIndicator
import pandas as pd

class EMA(MarketIndicator):
    def __init__(self, ohlcv: pd.DataFrame, term_n):
        self.term_n=term_n
        super().__init__(ohlcv)

    def calculate_indicator(self, ohlcv:pd.DataFrame) -> pd.Series:
        return ohlcv['close'].transform(lambda x:x.ewm(span=self.term_n).mean())

