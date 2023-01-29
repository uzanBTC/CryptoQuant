import backtrader as bt
from datetime import datetime

class OnBalanceVolume(bt.Indicator):
    '''
    REQUIREMENTS
    ----------------------------------------------------------------------
    Investopedia:
    ----------------------------------------------------------------------
    https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:on_balance_volume_obv

    1. If today's closing price is higher than yesterday's closing price,
       then: Current OBV = Previous OBV + today's volume

    2. If today's closing price is lower than yesterday's closing price,
       then: Current OBV = Previous OBV - today's volume

    3. If today's closing price equals yesterday's closing price,
       then: Current OBV = Previous OBV
    ----------------------------------------------------------------------
    '''

    alias = 'OBV'
    lines = ('obv',)

    plotlines = dict(
        obv=dict(
            _name='OBV',
            color='purple',
            alpha=0.50
        )
    )

    def __init__(self):

        # Plot a horizontal Line
        self.plotinfo.plotyhlines = [0]

    def nextstart(self):
        # We need to use next start to provide the initial value. This is because
        # we do not have a previous value for the first calcuation. These are
        # known as seed values.

        # Create some aliases
        c = self.data.close
        v = self.data.volume
        obv = self.lines.obv

        if c[0] > c[-1]:
            obv[0] = v[0]
        elif c[0] < c[-1]:
            obv[0] = -v[0]
        else:
            obv[0] = 0

    def next(self):
        c = self.data.close
        v = self.data.volume
        obv = self.lines.obv
        if c[0] > c[-1]:
            obv[0] = obv[-1] + v[0]
        elif c[0] < c[-1]:
            obv[0] = obv[-1] - v[0]
        else:
            obv[0] = obv[-1]