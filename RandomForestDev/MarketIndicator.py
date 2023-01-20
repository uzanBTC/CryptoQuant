import abc
import pandas as pd


class MarketIndicator(abc.ABC):

    def __init__(self, holcv: pd.DataFrame):
        self._indicator = self.calculate_indicator(holcv.copy)

    @abc.abstractmethod
    def calculate_indicator(self, holcv) -> pd.Series:
        pass

    @property
    def indicator(self):
        return self._indicator

    def __getitem__(self, time_key):
        '''
        to make the object iterable
        :param time_key: time to retrieve the indicator
        :return:
        '''
        return self._indicator[time_key]

    def __repr__(self) -> str:
        return self._indicator.__repr__()

    def __str__(self):
        return self._indicator.__str__()
