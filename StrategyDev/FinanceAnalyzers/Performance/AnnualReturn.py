from __future__ import (absolute_import, division, print_function, unicode_literals)

from collections import OrderedDict

from backtrader.utils.py3 import range
from backtrader import Analyzer

class AnnualReturn(Analyzer):
    def stop(self):
        #当前年份的初始值是-1
        cur_year = -1
        # 开始的账户价值
        value_start = 0.0
        # 当前账户价值
        value_cur = 0.0
        # 结束时账户价值
        value_end = 0.0
        # 列表
        self.rets = list()
        # 字典
        self.ret = OrderedDict()

        # 在结束的时候，遍历历史交易数据的值
        for i in range(len(self.data) - 1, -1, -1):
            # 获取数据的时间
            dt = self.data.datetime.date(-i)
            # 获取当前账户的价值
            value_cur = self.strategy.stats.broker.value[-i]
            # 如果是新的一年
            if dt.year > cur_year:
                # 如果当前年份大于0，即不是第一年
                if cur_year >= 0:
                    annualret = (value_end / value_start) - 1.0
                    self.rets.append(annualret)
                    self.ret[cur_year] = annualret

                    value_start =value_end
                # 如果当前是第一年
                else:
                    value_start = value_cur

                cur_year = dt.year

            # No matter what, the last value is always the last loaded value
            value_end = value_cur

        # 如果当前年份没有数据，就计算一次，一般是最后一年
        if cur_year not in self.ret:
            annualret = (value_end / value_start) -1.0
            self.rets.append(annualret)
            self.ret[cur_year] = annualret

    def get_analysis(self):
        return self.ret

