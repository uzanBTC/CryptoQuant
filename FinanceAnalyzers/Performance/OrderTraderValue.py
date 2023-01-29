'''
做策略时，需要核对order, trade，并且需要做计算。抽象出来在analyzer里面。在cerebro运行结束后，取出来就可以了。
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import OrderedDict
from backtrader.utils.date import num2date
from backtrader import Analyzer


# 这个文件用于创建一个analyzer，来保存order、trade和value的数据
class OrderTradeValue(Analyzer):
    params = ()
    def __init__(self):
        super(OrderTradeValue, self).__init__()
        # 保存order、trade和value的数据
        self.ret = {}
        self.ret['orders'] = []
        self.ret['trades'] = []
        self.ret['values'] = {}

    def next(self):
        current_date = num2date(self.datas[0].datetime[0])  # .strftime("%Y-%m-%d")
        total_value = self.strategy.broker.get_value()
        self.ret['values'][current_date] = total_value

    def stop(self):
        pass

    def notify_order(self, order):
        self.ret['orders'].append(order)


    def notify_trade(self, trade):
        # 一个trade结束的时候输出信息
        self.ret['trades'].append(trade)

    # 上面这些函数，和在strategy里面的用法几乎一致，不需要过多的分析

    def get_analysis(self):
        '''用于获取analyzer运行的结果，self.rets'''
        return self.ret
