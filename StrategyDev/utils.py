import joblib
import pandas as pd


def model_load(path):
    rfc = joblib.load(path)
    return rfc


def convert_csv_to_dataframe(csv_path):
    dataframe = pd.read_csv(csv_path)
    dataframe['time'] = pd.to_datetime(dataframe['time'])
    dataframe.set_index('time', inplace=True)
    return dataframe