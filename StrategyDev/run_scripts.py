import backtrader as bt
from pylab import mpl
import datetime as dt
import numpy as np

import warnings

from StrategyDev.RFStrategy import RFStrategy
from StrategyDev.FinanceAnalyzers.CerebroAnalyzers import add_analyzers_to_bt_cerebro, cerebro_result_visualizer
from StrategyDev.Indicators.OnBalanceVolume import OnBalanceVolume
from StrategyDev.utils import model_load, convert_csv_to_dataframe

def run_rf_strategy_plot(data_path, printlog=True ,startcash=10000000, com=0.0005):
    '''

    Strategy for Random Forest Model
    :param data_path:
    :param printlog:
    :param startcash:
    :param com:
    :return:
    '''
    cerebro = bt.Cerebro()
    rfc = model_load("rfc_finance_market.joblib")
    cerebro.addstrategy(RFStrategy,model=rfc, printlog=printlog)
    add_analyzers_to_bt_cerebro(cerebro)

    df = convert_csv_to_dataframe(data_path)

    data = bt.feeds.PandasData(dataname=df, fromdate=dt.datetime(2019, 8, 17),
                                    todate=dt.datetime(2022,12, 24), timeframe=bt.TimeFrame.Days)

    cerebro.adddata(data)
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission=com)
    cerebro.addsizer(bt.sizers.PercentSizer,percents=90)
    print('期初总资金: %.2f' % cerebro.broker.getvalue())
    result = cerebro.run()

    cerebro_result_visualizer(result,"results")

    cerebro.plot()

if __name__ == "__main__":
    run_rf_strategy_plot("data/price_data_bnb.csv")

 