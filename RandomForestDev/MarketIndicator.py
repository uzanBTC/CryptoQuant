import abc
import pandas as pd


class MarketIndicator(abc.ABC):

    def __init__(self, ohlcv: pd.DataFrame):
        if list(ohlcv.columns) != ['open', 'high', 'low', 'close', 'volume']:
            raise RuntimeError("Data Frame columns` value must be ['open','high','low','close','volume'] ")
        self._indicator = self.calculate_indicator(ohlcv.copy())

    @abc.abstractmethod
    def calculate_indicator(self, ohlcv) -> pd.Series:
        pass

    @property
    def indicator(self):
        '''
        only getter available
        :return: pandas.Series
        '''
        return self._indicator

    def __getitem__(self, pos):
        '''
        to make the object iterable
        :param pos: pos to retrieve the indicator
        :return:
        '''
        return self._indicator.index[pos], self._indicator[pos]

    def __repr__(self) -> str:
        return self._indicator.__repr__()

    def __str__(self):
        return self._indicator.__str__()
