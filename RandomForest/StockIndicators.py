import os
import sys
import requests

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import RocCurveDisplay
from sklearn.metrics import accuracy_score, classification_report

from config import ACCOUNT_NUMBER, ACCOUNT_PASSWORD, CONSUMER_ID, REDIRECT_URI

class StockIndicators():

    def __init__(self,holc:pd.DataFrame):
        self.holc=holc

    def get_rsi(self,n = 14) -> pd.DataFrame:
        price_data = self.holc.copy()
        up_df, down_df = price_data[['change_in_price']], price_data[['change_in_price']]

        # For up days, if the change is less than 0 set to 0
        up_df.loc['change_in_price'] = up_df.loc[(up_df['change_in_price'] < 0), 'change_in_price'] = 0

        # For down days, if the change is greater than 0 than set to 0.
        down_df.loc['change_in_price'] = down_df.loc[(down_df['change_in_price'] > 0), 'change_in_price'] = 0

        # We need change in price to be absolute
        down_df['change_in_price'] = down_df['change_in_price'].abs()

        # calculate the EMA
        ema_up = up_df['change_in_price'].transform(lambda x: x.ewm(span=n).mean())
        ema_down = down_df['change_in_price'].transform(lambda x: x.ewm(span=n).mean())

        # Calculate the relative strength
        relative_strength = ema_up / ema_down

        # Calculate the Relative index
        relative_strength_index = 100.0 - (100.0 / (1.0 + relative_strength))

        # Add the info to the data frame
        price_data['down_days'] = down_df['change_in_price']
        price_data['up_days'] = up_df['change_in_price']
        price_data['RSI'] = relative_strength_index
        #todo: 这里查看一下输出的格式是什么
        return price_data['RSI']

    def get_stochastic_oscillator(self,n=14):
        price_data = self.holc.copy()
        low_14, high_14 = price_data[['low']].copy(), price_data[['high']].copy()

        # Group by symbol, then apply the rolling function and grab the Min and Max.
        low_14 = low_14['low'].transform(lambda x: x.rolling(window=n).min())
        high_14 = high_14['high'].transform(lambda x: x.rolling(window=n).max())

        # Calculate the Stochastic Oscillator.
        k_percent = 100 * ((price_data['close'] - low_14) / (high_14 - low_14))

        # Add the info to the data frame.
        price_data['low_14'] = low_14
        price_data['high_14'] = high_14
        price_data['k_percent'] = k_percent
        return price_data['k_percent']

    def get_williams(self,n=14):
        price_data = self.holc.copy()
        # Make a copy of the high and low column.
        low_14, high_14 = price_data[['low']].copy(), price_data[['high']].copy()

        # Group by symbol, then apply the rolling function and grab the Min and Max.
        low_14 = low_14['low'].transform(lambda x: x.rolling(window=n).min())
        high_14 = high_14['high'].transform(lambda x: x.rolling(window=n).max())

        # Calculate William %R indicator.
        r_percent = ((high_14 - price_data['close']) / (high_14 - low_14)) * - 100

        # Add the info to the data frame.
        price_data['r_percent'] = r_percent
        return price_data['r_percent']

    def get_macd(self,long=26,short=12,avgterm=9):
        price_data = self.holc.copy()
        ema_26 = price_data['close'].transform(lambda x: x.ewm(span=long).mean())
        ema_12 = price_data['close'].transform(lambda x: x.ewm(span=short).mean())
        macd = ema_12 - ema_26

        # Calculate the EMA
        ema_9_macd = macd.ewm(span=avgterm).mean()

        # Store the data in the data frame.
        price_data['MACD'] = macd
        price_data['MACD_EMA'] = ema_9_macd
        return price_data['MACD'], price_data['MACD_EMA']

    def get_obv(self):
        price_data = self.holc.copy()
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