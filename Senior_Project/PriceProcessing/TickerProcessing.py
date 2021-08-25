
import pandas as pd
import numpy as np

'''

This class is going to have methods to process raw data given 
to develop features


'''
class TickerProcessing:

    '''
    params:
        price_series -> raw data to operate on
        distance -> number of candles passed after which, if price fails to make a new HIGH,
                    a candle is considered an extreme
        extrema_type -> specify whether you want to find high or lows
                    
    To perform linear regression well (meaning draw a clear trendline) 
    more than once on one chart, I need to be able to assign starting points
    and end points to the lines.

    returns:
        extrema_only
    '''
    def improved_identify_extremas(self, price_series : pd.Series(), distance, extrema_type):

        # if too short, don't consider it
        if len(price_series) <= distance * 4:
            return pd.Series()

        if extrema_type == "high" or extrema_type == "low":
            prepop_boolean = np.array([False] * len(price_series))
            extrema_series = pd.Series(data=prepop_boolean)
        else:
            raise ValueError("Only 'high' or 'low' allowed for 'extrema_type' arg" ) 

        for i in range(len(price_series)):
            # skip to avoid index out of bounds
            if i < distance * 2:
                continue
            # get earliest value of the distance specified
            earliest_index = i - distance * 2
            if extrema_type == "high":
                most_extreme_price = price_series.loc[earliest_index : i].max()
            else:
                most_extreme_price = price_series.loc[earliest_index : i].min()
            n_index = i - distance
            price_n_distance = price_series.at[n_index]

            # compare if earlist is the most extreme in the range given
            if price_n_distance == most_extreme_price:
                extrema_series.at[n_index] = True
        
        # the ends of the period are not reliable, due to the lack of data
        extrema_series.loc[:distance*2] = False
        extrema_series.loc[len(price_series)-distance:] = False

        return extrema_series

    '''
    params:
        series_high -> series of highs of each candle to find extremas of
        series_low -> series of lows of each candle to find extremas of 
        distance -> number of candles passed after which, if price fails to make a new extreme 
                    high or low, a candle is considered an extreme

    usually you are gonna want to get both highs and lows for a given stock.
    thus this function calls identify_lows_highs with both params low and the high, keeping the same
    distance and concatanating the two together.

    returns:
        dictionary of high extremas and low extremas

    '''
    def get_both_lows_highs(self, series_high, series_low, distance):
        extrema_high = self.improved_identify_extremas(series_high, distance=distance, extrema_type="high")
        extrema_low = self.improved_identify_extremas(series_low, distance=distance, extrema_type="low")

        return {"high": extrema_high, "low": extrema_low}

    '''
    params:
        extrema_df -> must have columns with highs and lows
        extrema -> either highs "h" or lows "l"
        above_last_num_highs -> number of n previous highs/lows you want current extrema to be higher than

    In order to draw valid trendlines, I only want to draw trendlines of stock that are
    in a trend. This particular function filters existing lows and highs to leave only those
    that are above its preceding n-lows or n-highs, respectively.

    Can get either higher highs or higher lows

    returns:
        higher_highs_and_lows -> only higher highs portion

    '''
    def get_higher_extrema(self, ohlc_df:pd.DataFrame(), extrema:str(), distance:int(), above_last_num_highs:int()):
        # get all highs only
        highs_df = ohlc_df[ohlc_df[f"{extrema}_extremes_{distance}"]==True]
        higher_extrema_query = ""
        for cons_high in range(1, above_last_num_highs+1):
            # find the difference between current high and n previous high
            highs_df[f"h{extrema}{cons_high}"] = highs_df[extrema].diff(cons_high)
            higher_extrema_query = higher_extrema_query + f" h{extrema}{cons_high} > 0 &"

        # take out last "&"
        higher_extrema_query = higher_extrema_query[:-1]

        # select highs to remove (their difference is negative)
        higher_highs = highs_df.query(higher_extrema_query)

        return higher_highs

    '''
    params:
        ticker_volume_series -> "v" volume column only
        distance -> range of candles
    
    This function calculates average volume for a ticker (agnostic to timeframe and its multiple)

    returns:
        average_v_series
    '''
    def get_average_volume(self, ticker_volume_series: pd.Series(), distance):

        average_v_series = ticker_volume_series.rolling(distance).mean()

        return average_v_series

