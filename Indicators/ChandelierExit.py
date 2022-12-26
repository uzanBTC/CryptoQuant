import backtrader as bt


class ChandelierExit(bt.Indicator):
    lines = ('long', 'short')
    params = (('period', 12), ('multip', 3),)

    plot_info = dict(subplot=False)

    def __init__(self):
        highest = bt.ind.Highest(self.data.high, period=self.p.period)
        lowest = bt.ind.Lowest(self.data.low, period=self.p.period)
        atr = self.p.multip * bt.ind.ATR(self.data, period=self.p.period)
        self.lines.long = highest - atr
        self.lines.short = lowest + atr
