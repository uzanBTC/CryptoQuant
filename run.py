# -*- coding: utf-8 -*-
from datetime import datetime
import os
from collections import OrderedDict
import backtrader as bt
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dcc, dash_table
from jupyter_plotly_dash import JupyterDash
from openpyxl import load_workbook

from ClassicStrategy.turtleStrategy import TradeSizer, TurtleStrategy
from Performance.TotalValue import TotalValue

import backtrader as bt
import matplotlib
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
from pyecharts.charts import Line, Bar
from pylab import mpl

import datetime as dt

from StrategyDev.ATRVegasStrategy import ATRVegasStrategy

'''
Note:
If you only have 1 year of data and taking into account that the default timeframe for the calculation is years, no calculation can take place. Sharpe needs at least 2 samples for the given timeframe, to calculate the variance.
'''


def add_analyzers(cerebro):
    # cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    cerebro.addanalyzer(TotalValue, _name='_TotalValue')
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='_AnnualReturn')
    cerebro.addanalyzer(bt.analyzers.Calmar, _name='_Calmar')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='_DrawDown')
    cerebro.addanalyzer(bt.analyzers.TimeDrawDown, _name='_TimeDrawDown')
    cerebro.addanalyzer(bt.analyzers.GrossLeverage, _name='_GrossLeverage')
    cerebro.addanalyzer(bt.analyzers.PositionsValue, _name='_PositionsValue')
    cerebro.addanalyzer(bt.analyzers.LogReturnsRolling, _name='_LogReturnsRolling')
    cerebro.addanalyzer(bt.analyzers.PeriodStats, _name='_PeriodStats')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='_Returns')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_SharpeRatio')
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name='_SharpeRatio_A')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='_SQN')
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='_TimeReturn')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='_TradeAnalyzer')
    cerebro.addanalyzer(bt.analyzers.Transactions, _name='_Transactions')
    cerebro.addanalyzer(bt.analyzers.VWR, _name='_VWR')


def out_result(strategy, data, sizer, startcash=1000000.0, commission=0.001):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)
    cerebro.adddata(data)
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission)
    if(sizer is None):
        cerebro.addsizer(bt.sizers.PercentSizer, percents=90)
    else:
        cerebro.addsizer(sizer)

    add_analyzers(cerebro)

    results = cerebro.run()

    performance_dict = OrderedDict()
    calmar_ratio = list(results[0].analyzers._Calmar.get_analysis().values())[-1]
    drawdown_info = results[0].analyzers._DrawDown.get_analysis()
    average_drawdown_len = drawdown_info['len']
    average_drawdown_rate = drawdown_info['drawdown']
    average_drawdown_money = drawdown_info['moneydown']
    max_drawdown_len = drawdown_info['max']['len']
    max_drawdown_rate = drawdown_info['max']['drawdown']
    max_drawdown_money = drawdown_info['max']['moneydown']
    PeriodStats_info = results[0].analyzers._PeriodStats.get_analysis()
    average_rate = PeriodStats_info['average']
    stddev_rate = PeriodStats_info['stddev']
    positive_year = PeriodStats_info['positive']
    negative_year = PeriodStats_info['negative']
    nochange_year = PeriodStats_info['nochange']
    best_year = PeriodStats_info['best']
    worst_year = PeriodStats_info['worst']
    SQN_info = results[0].analyzers._SQN.get_analysis()
    sqn_ratio = SQN_info['sqn']
    VWR_info = results[0].analyzers._VWR.get_analysis()
    vwr_ratio = VWR_info['vwr']

    sharpe_info = results[0].analyzers._SharpeRatio.get_analysis()
    # sharpe_info=results[0].analyzers._SharpeRatio_A.get_analysis()
    print(sharpe_info)
    sharpe_ratio = sharpe_info['sharperatio']

    performance_dict['calmar_ratio'] = round(calmar_ratio * 100, 3)
    performance_dict['average_drawdown_len'] = average_drawdown_len
    performance_dict['average_drawdown_rate'] = round(average_drawdown_rate, 2)
    performance_dict['average_drawdown_money'] = round(average_drawdown_money, 2)
    performance_dict['max_drawdown_len'] = max_drawdown_len
    performance_dict['max_drawdown_rate'] = round(max_drawdown_rate, 2)
    performance_dict['max_drawdown_money'] = round(max_drawdown_money, 2)
    performance_dict['average_rate'] = round(average_rate, 2)
    performance_dict['stddev_rate'] = round(stddev_rate, 2)
    performance_dict['positive_year'] = positive_year
    performance_dict['negative_year'] = negative_year
    performance_dict['nochange_year'] = nochange_year
    performance_dict['best_year'] = round(best_year * 100, 2)
    performance_dict['worst_year'] = round(worst_year * 100, 2)
    performance_dict['sqn_ratio'] = round(sqn_ratio, 2)
    performance_dict['vwr_ratio'] = round(vwr_ratio, 2)
    performance_dict['sharpe_info'] = round(sharpe_ratio, 2)
    performance_dict['omega'] = 0

    trade_dict_1 = OrderedDict()
    trade_dict_2 = OrderedDict()
    trade_info = results[0].analyzers._TradeAnalyzer.get_analysis()
    total_trade_num = trade_info['total']['total']
    total_trade_opened = trade_info['total']['open']
    total_trade_closed = trade_info['total']['closed']
    total_trade_len = trade_info['len']['total']
    long_trade_len = trade_info['len']['long']['total']
    short_trade_len = trade_info['len']['short']['total']

    longest_win_num = trade_info['streak']['won']['longest']
    longest_lost_num = trade_info['streak']['lost']['longest']
    net_total_pnl = trade_info['pnl']['net']['total']
    net_average_pnl = trade_info['pnl']['net']['average']
    win_num = trade_info['won']['total']
    win_total_pnl = trade_info['won']['pnl']['total']
    win_average_pnl = trade_info['won']['pnl']['average']
    win_max_pnl = trade_info['won']['pnl']['max']
    lost_num = trade_info['lost']['total']
    lost_total_pnl = trade_info['lost']['pnl']['total']
    lost_average_pnl = trade_info['lost']['pnl']['average']
    lost_max_pnl = trade_info['lost']['pnl']['max']

    trade_dict_1['total_trade_num'] = total_trade_num
    trade_dict_1['total_trade_opened'] = total_trade_opened
    trade_dict_1['total_trade_closed'] = total_trade_closed
    trade_dict_1['total_trade_len'] = total_trade_len
    trade_dict_1['long_trade_len'] = long_trade_len
    trade_dict_1['short_trade_len'] = short_trade_len
    trade_dict_1['longest_win_num'] = longest_win_num
    trade_dict_1['longest_lost_num'] = longest_lost_num
    trade_dict_1['net_total_pnl'] = net_total_pnl
    trade_dict_1['net_average_pnl'] = net_average_pnl
    trade_dict_1['win_num'] = win_num
    trade_dict_1['win_total_pnl'] = win_total_pnl
    trade_dict_1['win_average_pnl'] = win_average_pnl
    trade_dict_1['win_max_pnl'] = win_max_pnl
    trade_dict_1['lost_num'] = lost_num
    trade_dict_1['lost_total_pnl'] = lost_total_pnl
    trade_dict_1['lost_average_pnl'] = lost_average_pnl
    trade_dict_1['lost_max_pnl'] = lost_max_pnl

    long_num = trade_info['long']['total']
    long_win_num = trade_info['long']['won']
    long_lost_num = trade_info['long']['lost']
    long_total_pnl = trade_info['long']['pnl']['total']
    long_average_pnl = trade_info['long']['pnl']['average']
    long_win_total_pnl = trade_info['long']['pnl']['won']['total']
    long_win_max_pnl = trade_info['long']['pnl']['won']['max']
    long_lost_total_pnl = trade_info['long']['pnl']['lost']['total']
    long_lost_max_pnl = trade_info['long']['pnl']['lost']['max']

    short_num = trade_info['short']['total']
    short_win_num = trade_info['short']['won']
    short_lost_num = trade_info['short']['lost']
    short_total_pnl = trade_info['short']['pnl']['total']
    short_average_pnl = trade_info['short']['pnl']['average']
    short_win_total_pnl = trade_info['short']['pnl']['won']['total']
    short_win_max_pnl = trade_info['short']['pnl']['won']['max']
    short_lost_total_pnl = trade_info['short']['pnl']['lost']['total']
    short_lost_max_pnl = trade_info['short']['pnl']['lost']['max']

    trade_dict_2['long_num'] = long_num
    trade_dict_2['long_win_num'] = long_win_num
    trade_dict_2['long_lost_num'] = long_lost_num
    trade_dict_2['long_total_pnl'] = long_total_pnl
    trade_dict_2['long_average_pnl'] = long_average_pnl
    trade_dict_2['long_win_total_pnl'] = long_win_total_pnl
    trade_dict_2['long_win_max_pnl'] = long_win_max_pnl
    trade_dict_2['long_lost_total_pnl'] = long_lost_total_pnl
    trade_dict_2['long_lost_max_pnl'] = long_lost_max_pnl
    trade_dict_2['short_num'] = short_num
    trade_dict_2['short_win_num'] = short_win_num
    trade_dict_2['short_lost_num'] = short_lost_num
    trade_dict_2['short_total_pnl'] = short_total_pnl
    trade_dict_2['short_average_pnl'] = short_average_pnl
    trade_dict_2['short_win_total_pnl'] = short_win_total_pnl
    trade_dict_2['short_win_max_pnl'] = short_win_max_pnl
    trade_dict_2['short_lost_total_pnl'] = short_lost_total_pnl
    trade_dict_2['short_lost_max_pnl'] = short_lost_max_pnl

    df_ratio_overview = pd.DataFrame(index=range(len(performance_dict)))
    df01 = pd.DataFrame([performance_dict]).T
    df01.columns = ['绩效指标值']
    df02 = pd.DataFrame([trade_dict_1]).T
    df02.columns = ['普通交易指标值']
    df03 = pd.DataFrame([trade_dict_2]).T
    df03.columns = ['多空交易指标值']
    df_ratio_overview['绩效指标'] = df01.index
    df_ratio_overview['绩效指标值'] = df01.round(4).values
    df_ratio_overview['普通交易指标'] = df02.index
    df_ratio_overview['普通交易指标值'] = [round(float(i), 4) for i in list(df02['普通交易指标值'])]
    df_ratio_overview['多空交易指标'] = df03.index
    df_ratio_overview['多空交易指标值'] = [round(float(i), 4) for i in list(df03['多空交易指标值'])]

    # 账户收益率
    df_total_value = pd.DataFrame([results[0].analyzers._TotalValue.get_analysis()]).T
    df_total_value.columns = ['total_value']

    # 总的杠杆
    df_gross_leverage = pd.DataFrame([results[0].analyzers._GrossLeverage.get_analysis()]).T
    df_gross_leverage.columns = ['GrossLeverage']

    # 滚动的对数收益率
    df_log_return = pd.DataFrame([results[0].analyzers._LogReturnsRolling.get_analysis()]).T
    df_log_return.columns = ['log_return']

    # year_rate
    df_year_rate = pd.DataFrame([results[0].analyzers._AnnualReturn.get_analysis()]).T
    df_year_rate.columns = ['year_rate']

    # 总的持仓价值
    df_total_position_value = pd.DataFrame(results[0].analyzers._PositionsValue.get_analysis()).T
    df_total_position_value['total_position_value'] = df_total_position_value.sum(axis=1)

    # pyfoliozer = results[0].analyzers.getbyname('pyfolio')
    # returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    return df_ratio_overview, df_total_value, df_gross_leverage, df_log_return, df_year_rate, df_total_position_value


def result_handler(results):
    performance_dict = OrderedDict()
    calmar_ratio = list(results[0].analyzers._Calmar.get_analysis().values())[-1]
    drawdown_info = results[0].analyzers._DrawDown.get_analysis()
    average_drawdown_len = drawdown_info['len']
    average_drawdown_rate = drawdown_info['drawdown']
    average_drawdown_money = drawdown_info['moneydown']
    max_drawdown_len = drawdown_info['max']['len']
    max_drawdown_rate = drawdown_info['max']['drawdown']
    max_drawdown_money = drawdown_info['max']['moneydown']
    PeriodStats_info = results[0].analyzers._PeriodStats.get_analysis()
    average_rate = PeriodStats_info['average']
    stddev_rate = PeriodStats_info['stddev']
    positive_year = PeriodStats_info['positive']
    negative_year = PeriodStats_info['negative']
    nochange_year = PeriodStats_info['nochange']
    best_year = PeriodStats_info['best']
    worst_year = PeriodStats_info['worst']
    SQN_info = results[0].analyzers._SQN.get_analysis()
    sqn_ratio = SQN_info['sqn']
    VWR_info = results[0].analyzers._VWR.get_analysis()
    vwr_ratio = VWR_info['vwr']

    sharpe_info = results[0].analyzers._SharpeRatio.get_analysis()
    # sharpe_info=results[0].analyzers._SharpeRatio_A.get_analysis()
    print(sharpe_info)
    sharpe_ratio = sharpe_info['sharperatio']

    performance_dict['calmar_ratio'] = round(calmar_ratio * 100, 3)
    performance_dict['average_drawdown_len'] = average_drawdown_len
    performance_dict['average_drawdown_rate'] = round(average_drawdown_rate, 2)
    performance_dict['average_drawdown_money'] = round(average_drawdown_money, 2)
    performance_dict['max_drawdown_len'] = max_drawdown_len
    performance_dict['max_drawdown_rate'] = round(max_drawdown_rate, 2)
    performance_dict['max_drawdown_money'] = round(max_drawdown_money, 2)
    performance_dict['average_rate'] = round(average_rate, 2)
    performance_dict['stddev_rate'] = round(stddev_rate, 2)
    performance_dict['positive_year'] = positive_year
    performance_dict['negative_year'] = negative_year
    performance_dict['nochange_year'] = nochange_year
    performance_dict['best_year'] = round(best_year * 100, 2)
    performance_dict['worst_year'] = round(worst_year * 100, 2)
    performance_dict['sqn_ratio'] = round(sqn_ratio, 2)
    performance_dict['vwr_ratio'] = round(vwr_ratio, 2)
    performance_dict['sharpe_info'] = round(sharpe_ratio, 2)
    performance_dict['omega'] = 0

    trade_dict_1 = OrderedDict()
    trade_dict_2 = OrderedDict()
    trade_info = results[0].analyzers._TradeAnalyzer.get_analysis()
    total_trade_num = trade_info['total']['total']
    total_trade_opened = trade_info['total']['open']
    total_trade_closed = trade_info['total']['closed']
    total_trade_len = trade_info['len']['total']
    long_trade_len = trade_info['len']['long']['total']
    short_trade_len = trade_info['len']['short']['total']

    longest_win_num = trade_info['streak']['won']['longest']
    longest_lost_num = trade_info['streak']['lost']['longest']
    net_total_pnl = trade_info['pnl']['net']['total']
    net_average_pnl = trade_info['pnl']['net']['average']
    win_num = trade_info['won']['total']
    win_total_pnl = trade_info['won']['pnl']['total']
    win_average_pnl = trade_info['won']['pnl']['average']
    win_max_pnl = trade_info['won']['pnl']['max']
    lost_num = trade_info['lost']['total']
    lost_total_pnl = trade_info['lost']['pnl']['total']
    lost_average_pnl = trade_info['lost']['pnl']['average']
    lost_max_pnl = trade_info['lost']['pnl']['max']

    trade_dict_1['total_trade_num'] = total_trade_num
    trade_dict_1['total_trade_opened'] = total_trade_opened
    trade_dict_1['total_trade_closed'] = total_trade_closed
    trade_dict_1['total_trade_len'] = total_trade_len
    trade_dict_1['long_trade_len'] = long_trade_len
    trade_dict_1['short_trade_len'] = short_trade_len
    trade_dict_1['longest_win_num'] = longest_win_num
    trade_dict_1['longest_lost_num'] = longest_lost_num
    trade_dict_1['net_total_pnl'] = net_total_pnl
    trade_dict_1['net_average_pnl'] = net_average_pnl
    trade_dict_1['win_num'] = win_num
    trade_dict_1['win_total_pnl'] = win_total_pnl
    trade_dict_1['win_average_pnl'] = win_average_pnl
    trade_dict_1['win_max_pnl'] = win_max_pnl
    trade_dict_1['lost_num'] = lost_num
    trade_dict_1['lost_total_pnl'] = lost_total_pnl
    trade_dict_1['lost_average_pnl'] = lost_average_pnl
    trade_dict_1['lost_max_pnl'] = lost_max_pnl

    long_num = trade_info['long']['total']
    long_win_num = trade_info['long']['won']
    long_lost_num = trade_info['long']['lost']
    long_total_pnl = trade_info['long']['pnl']['total']
    long_average_pnl = trade_info['long']['pnl']['average']
    long_win_total_pnl = trade_info['long']['pnl']['won']['total']
    long_win_max_pnl = trade_info['long']['pnl']['won']['max']
    long_lost_total_pnl = trade_info['long']['pnl']['lost']['total']
    long_lost_max_pnl = trade_info['long']['pnl']['lost']['max']

    short_num = trade_info['short']['total']
    short_win_num = trade_info['short']['won']
    short_lost_num = trade_info['short']['lost']
    short_total_pnl = trade_info['short']['pnl']['total']
    short_average_pnl = trade_info['short']['pnl']['average']
    short_win_total_pnl = trade_info['short']['pnl']['won']['total']
    short_win_max_pnl = trade_info['short']['pnl']['won']['max']
    short_lost_total_pnl = trade_info['short']['pnl']['lost']['total']
    short_lost_max_pnl = trade_info['short']['pnl']['lost']['max']

    trade_dict_2['long_num'] = long_num
    trade_dict_2['long_win_num'] = long_win_num
    trade_dict_2['long_lost_num'] = long_lost_num
    trade_dict_2['long_total_pnl'] = long_total_pnl
    trade_dict_2['long_average_pnl'] = long_average_pnl
    trade_dict_2['long_win_total_pnl'] = long_win_total_pnl
    trade_dict_2['long_win_max_pnl'] = long_win_max_pnl
    trade_dict_2['long_lost_total_pnl'] = long_lost_total_pnl
    trade_dict_2['long_lost_max_pnl'] = long_lost_max_pnl
    trade_dict_2['short_num'] = short_num
    trade_dict_2['short_win_num'] = short_win_num
    trade_dict_2['short_lost_num'] = short_lost_num
    trade_dict_2['short_total_pnl'] = short_total_pnl
    trade_dict_2['short_average_pnl'] = short_average_pnl
    trade_dict_2['short_win_total_pnl'] = short_win_total_pnl
    trade_dict_2['short_win_max_pnl'] = short_win_max_pnl
    trade_dict_2['short_lost_total_pnl'] = short_lost_total_pnl
    trade_dict_2['short_lost_max_pnl'] = short_lost_max_pnl

    df_ratio_overview = pd.DataFrame(index=range(len(performance_dict)))
    df01 = pd.DataFrame([performance_dict]).T
    df01.columns = ['绩效指标值']
    df02 = pd.DataFrame([trade_dict_1]).T
    df02.columns = ['普通交易指标值']
    df03 = pd.DataFrame([trade_dict_2]).T
    df03.columns = ['多空交易指标值']
    df_ratio_overview['绩效指标'] = df01.index
    df_ratio_overview['绩效指标值'] = df01.round(4).values
    df_ratio_overview['普通交易指标'] = df02.index
    df_ratio_overview['普通交易指标值'] = [round(float(i), 4) for i in list(df02['普通交易指标值'])]
    df_ratio_overview['多空交易指标'] = df03.index
    df_ratio_overview['多空交易指标值'] = [round(float(i), 4) for i in list(df03['多空交易指标值'])]

    # 账户收益率
    df_total_value = pd.DataFrame([results[0].analyzers._TotalValue.get_analysis()]).T
    df_total_value.columns = ['total_value']

    # 总的杠杆
    df_gross_leverage = pd.DataFrame([results[0].analyzers._GrossLeverage.get_analysis()]).T
    df_gross_leverage.columns = ['GrossLeverage']

    # 滚动的对数收益率
    df_log_return = pd.DataFrame([results[0].analyzers._LogReturnsRolling.get_analysis()]).T
    df_log_return.columns = ['log_return']

    # year_rate
    df_year_rate = pd.DataFrame([results[0].analyzers._AnnualReturn.get_analysis()]).T
    df_year_rate.columns = ['year_rate']

    # 总的持仓价值
    df_total_position_value = pd.DataFrame(results[0].analyzers._PositionsValue.get_analysis()).T
    df_total_position_value['total_position_value'] = df_total_position_value.sum(axis=1)

    # pyfoliozer = results[0].analyzers.getbyname('pyfolio')
    # returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    return df_ratio_overview, df_total_value, df_gross_leverage, df_log_return, df_year_rate, df_total_position_value


def create_table(df):
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],
        style_as_list_view=True,
        style_cell={
            'height': 'auto',
            'whiteSpace': 'normal'
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left',
                'width': '250px'

            } for c in df.columns
        ],
    )


def plot_result(strategy, data, sizer, startcash=100000, commission=0.001):
    # df_ratio_overview, df_total_value, df_gross_leverage, df_log_return, df_year_rate, df_total_position_value = out_result(strategy, data, sizer, startcash=startcash, commission=commission)
    df_ratio_overview, df_total_value, df_gross_leverage, df_log_return, df_year_rate, df_total_position_value = out_result(
        strategy, data, sizer, startcash=startcash, commission=commission)
    save_df_to_excel(df_ratio_overview, df_total_value, df_gross_leverage, df_log_return, df_year_rate,
                     df_total_position_value)
    print("-------")
    print(df_ratio_overview)
    return performance_dt_to_dash(df_ratio_overview, df_total_value, df_year_rate,
                                  df_total_position_value)


def save_df_to_excel(df_ratio_overview, df_total_value, df_gross_leverage, df_log_return, df_year_rate,
                     df_total_position_value):
    report_path = "performance-output-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    if not os.path.exists(report_path):
        os.makedirs(report_path)

    path = os.path.join(report_path, 'system_performance_data.xlsx')

    writer = pd.ExcelWriter(path, engine='openpyxl', mode='w')

    df_ratio_overview.to_excel(writer,
                               sheet_name="df_ratio_overview")

    df_total_value.to_excel(writer,
                            sheet_name="df_total_value")

    df_year_rate.to_excel(writer,
                          sheet_name="df_year_rate")
    df_total_position_value.to_excel(writer,
                                     sheet_name="df_total_position_value")

    writer.close()


def excel_to_dash_app(path):
    d1,d2,d3,d4=excel_to_performance_data(path)
    return performance_dt_to_dash(d1,d2,d3,d4)

def excel_to_performance_data(path):
    df_sheet_overview = pd.read_excel(path, sheet_name="df_ratio_overview")

    df_total_value = pd.read_excel(path, sheet_name="df_total_value")

    df_year_rate = pd.read_excel(path, sheet_name="df_year_rate")

    df_total_position_value = pd.read_excel(path, sheet_name="df_total_position_value")

    return df_sheet_overview.iloc[:, 1:], df_total_value.iloc[:, 1:], df_year_rate.iloc[:, 1:], df_total_position_value.iloc[:, 2:]


def performance_dt_to_dash(df_ratio_overview, df_total_value, df_year_rate, df_total_position_value):
    # app = dash('评价指标')
    app = Dash(__name__)
    colors = dict(background='white', text='black')
    strategy_name = "量化策略"
    app.layout = html.Div(
        style=dict(backgroundColor=colors['background']),
        children=[
            html.H1(
                children='{}策略评估结果'.format(strategy_name),
                style=dict(textAlign='center', color=colors['text'])),

            dcc.Graph(
                id='账户价值',
                figure=dict(
                    data=[{'x': list(df_total_value.index), 'y': list(df_total_value.total_value),
                           # 'text':[int(i*1000)/10 for i in list(df3.year_rate)],
                           'type': 'scatter', 'name': '账户价值',
                           'textposition': "outside"}],
                    layout=dict(
                        title='账户价值',
                        plot_bgcolor=colors['background'],
                        paper_bgcolor=colors['background'],
                        font=dict(color=colors['text'],
                                  )
                    )
                )
            ),

            dcc.Graph(
                id='持仓市值',
                figure=dict(
                    data=[{'x': list(df_total_position_value.index),
                           'y': list(df_total_position_value.total_position_value),
                           # 'text':[int(i*1000)/10 for i in list(df3.year_rate)],
                           'type': 'scatter', 'name': '持仓市值',
                           'textposition': "outside"}],
                    layout=dict(
                        title='持仓市值',
                        plot_bgcolor=colors['background'],
                        paper_bgcolor=colors['background'],
                        font=dict(color=colors['text']),
                    )
                )
            ),
            dcc.Graph(
                id='年化收益',
                figure=dict(
                    data=[{'x': list(df_year_rate.index), 'y': list(df_year_rate.year_rate),
                           'text': [int(i * 1000) / 10 for i in list(df_year_rate.year_rate)],
                           'type': 'bar', 'name': '年收益率',
                           'textposition': "outside"}],
                    layout=dict(
                        title='年化收益率',
                        plot_bgcolor=colors['background'],
                        paper_bgcolor=colors['background'],
                        font=dict(color=colors['text']),
                    )
                )
            ),
            create_table(df_ratio_overview)

        ]
    )

    return app


def performance(code, long, short, start, end, startcash, com):
    df = ts.get_k_data(code, autype='qfq', start=start, end=end)
    df.index = pd.to_datetime(df.date)
    df = df[['open', 'high', 'low', 'close', 'volume']]
    print("===")
    print(df)
    # 将数据加载至回测系统
    data = bt.feeds.PandasData(dataname=df)
    app = plot_result(TurtleStrategy, data, TradeSizer, startcash, com)
    return app

def convert_csv_to_dataframe(csv_path):
    dataframe = pd.read_csv(csv_path)
    dataframe['time'] = pd.to_datetime(dataframe['time'])
    dataframe.set_index('time', inplace=True)
    return dataframe

def atr_strategy_performance(startcash, com):

    df = convert_csv_to_dataframe('data/backtesting.csv')

    data = bt.feeds.PandasData(dataname=df, fromdate=dt.datetime(2019, 8, 17),
                               todate=dt.datetime(2022, 12, 5), timeframe=bt.TimeFrame.Days)

    app = plot_result(ATRVegasStrategy, data, None, startcash, com)
    return app



if __name__ == "__main__":
    # long_list = range(20, 70, 5)
    # short_list = range(5, 20, 5)
    # run('sh', long_list, short_list, '2010-01-01', '2020-07-17')
    # p_plot.out_result(TurtleStrategy)
    # app = performance('sh', 50, 5, '2010-01-01', '2021-07-17', 10000000, 0.001)
    # app.run_server(debug=False)
    '''print("========")
    path = "performance-output-20221223-114248/system_performance_data.xlsx"
    d1, d2, d3, d4 = excel_to_performance_data(path)
    print(d4)
    app = performance_dt_to_dash(d1,d2,d3,d4)
    app.run_server(debug=False)'''
    app = atr_strategy_performance(10000000, 0.0001)
    app.run_server(debug=False)

