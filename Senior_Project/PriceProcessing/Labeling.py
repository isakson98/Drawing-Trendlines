

import pandas as pd

'''

This class is going to be responsible for labeling trendlines' performance.
There are many ways to judge how a well trade went. It is possible to go
deep enough to include the sharpe ratio and other kinds of metrics, which would
be possible to implement in this class.

For the first type of label, I decided to go for this simple R/R, and whichever
one gets hit first will be labeled as such. This type of label will be a simple
binary classification (1 if price hits a target or 0 if price hits a stop loss).

This leads to further questions like, what is going to be my stop loss? what is going 
to be my target? Given more time, I would gladly dive deep into analysis of this 
question, but at this point, I am going to just eye ball it, and say that my stop loss
will be the low of either the breakout candle or the previous candle (whichever one is
lower). As for my target, I am going to go for a conservative 2.5 reward to be labeled 
as a sucessful trade

'''
class Labeling():

    '''
    params:
        trendline_df
        raw_df

    returns:
        series 
    '''
    def calculate_binary_label(self, trendline_df, raw_df, num_of_lows, profitable_r):

        # establish what is the low going to be
        lows_col_name = f"stop_loss_{num_of_lows}_num_of_lows"
        trendline_df[lows_col_name]=self.get_low_based_on_n_last_candles(trendline_df, raw_df, num_of_lows)

        # get the desire target price for the trendline
        trendline_df["entry_pos"] = self.get_entry_position(trendline_df, raw_df)
        profit_price_col_name = f"profit_price_{profitable_r}_profitable_r_{num_of_lows}_num_of_lows"
        trendline_df[profit_price_col_name] = self.calculate_target_price(trendline_df, lows_col_name, profitable_r)

        # check what gets hit first: target or stop loss
        outcome_series = self.check_trendline_outcome(trendline_df, raw_df, lows_col_name, profit_price_col_name)

        return outcome_series


    '''
    params:
        trendline_df -> df where rows are trendlines only
        raw_df -> regular raw df
        num_of_lows -> number of days to look to determine the stop loss

    purpose:
        given number of candles ago to look at, I pick the smallest value.
        ex. if num_of_lows is 2, i look at the lows of the breakout day and
        one day before, and pick the minimum for my stop loss price.

    returns:
        series of stop prices based on the max number of lows looked
    '''
    def get_low_based_on_n_last_candles(self, trendline_df, raw_df, num_of_lows):

        col_name = f"rolling_{num_of_lows}_num_of_lows"
        raw_df[col_name] = raw_df["l"].rolling(num_of_lows).min()
        
        trendline_and_raw_lows_df = pd.merge(left=trendline_df,
                                        left_on = trendline_df["t_end"],
                                        right=raw_df[col_name],
                                        right_on = raw_df["t"],
                                        how="left")
        
        return trendline_and_raw_lows_df[col_name]


    '''
    params:
        trendline_df -> df where rows are trendlines only
        raw_df -> 
    purpose:
        the entry will be end of day of breakout

    returns:
        return the series where each row is a profit price for the trendline
    '''
    def get_entry_position(self, trendline_df, raw_df):

        trendline_and_raw_lows_df = pd.merge(left=trendline_df,
                                        left_on = trendline_df["t_end"],
                                        right=raw_df["c"],
                                        right_on = raw_df["t"],
                                        how="left")
        
        return trendline_and_raw_lows_df["c"]

    '''
    params:
        trendline_df -> df where rows are trendlines only
        raw_df -> 

    purpose:
        calculating the target price

    returns:
        return the series where each row is a profit price for the trendline
    '''
    def calculate_target_price(self, trendline_df, lows_col_name, profitable_r):
        
        stop_loss_series = trendline_df[lows_col_name]
        end_of_trendline_series = trendline_df["entry_pos"]

        stop_entry_range = end_of_trendline_series - stop_loss_series
        profit_range = (stop_entry_range) * profitable_r

        profit_price = end_of_trendline_series + profit_range

        return profit_price



    def __helper_check_trendline_outcome(self, breakout_tmstmp, stop, profit, raw_df):
        df_after_breakout = raw_df[raw_df['t'] > breakout_tmstmp]
        needed_cols_df = df_after_breakout[["h", "l", "t"]]
        # itertuples is faster than iterrows, however, itertuples saves tuples, not dicts, so
        # i am handling above to always know the exact position f each column
        # also index one is always first, so I am removing cause i don't need it 
        for row in needed_cols_df.itertuples(index=False):
            if float(row[0]) >= profit:
                return True
            elif float(row[1]) <= stop:
                return False


    '''
    params:
        trendline_df -> df where rows are trendlines only
        raw_df -> sequential raw data
        lows_col_name -> parameterized column name of the stop price
        profit_price_col_name -> parameterized column name of the profit price

    purpose:
        this function determines whether the trade was succesfful or not based
        on what gets hit first 

    returns:
        return the series where each row is a profit price for the trendline
    '''
    def check_trendline_outcome(self, trendline_df, raw_df, lows_col_name, profit_price_col_name):

        label_series = trendline_df.apply(lambda row : self.__helper_check_trendline_outcome(
                                                                                            row["t_end"],
                                                                                            row[lows_col_name],
                                                                                            row[profit_price_col_name],
                                                                                            raw_df,
                                                                                            ),axis=1)
        return label_series


