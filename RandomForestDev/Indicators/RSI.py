from RandomForestDev.Indicators.MarketIndicator import MarketIndicator
import pandas as pd

class RSI(MarketIndicator):

    def __init__(self, ohlcv: pd.DataFrame,n=14):
        self.n=n
        super().__init__(ohlcv)

    def calculate_indicator(self, ohlcv) -> pd.Series:
        price_data = ohlcv
        price_data['change_in_price'] = price_data['close'].diff()
        up_df, down_df = price_data[['change_in_price']], price_data[['change_in_price']]

        # For up days, if the change is less than 0 set to 0
        up_df.loc['change_in_price'] = up_df.loc[(up_df['change_in_price'] < 0), 'change_in_price'] = 0

        # For down days, if the change is greater than 0 than set to 0.
        down_df.loc['change_in_price'] = down_df.loc[(down_df['change_in_price'] > 0), 'change_in_price'] = 0

        # We need change in price to be absolute
        down_df['change_in_price'] = down_df['change_in_price'].abs()

        # calculate the EMA
        ema_up = up_df['change_in_price'].transform(lambda x: x.ewm(span=self.n).mean())
        ema_down = down_df['change_in_price'].transform(lambda x: x.ewm(span=self.n).mean())

        # Calculate the relative strength
        relative_strength = ema_up / ema_down

        # Calculate the Relative index
        relative_strength_index = 100.0 - (100.0 / (1.0 + relative_strength))

        # Add the info to the data frame
        price_data['down_days'] = down_df['change_in_price']
        price_data['up_days'] = up_df['change_in_price']
        price_data['RSI'] = relative_strength_index
        return price_data['RSI']
 