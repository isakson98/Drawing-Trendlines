
import pandas as pd

'''

This class is going to have methods to process raw data given 
to develop features


'''
class TickerProcessing:

    '''
    params:
        extrema_type -> "h"/ "high" or "l" / "low" acceptable only, per naming conventions in the 
        distance -> number of candles passed after which, if price fails to make a new extreme 
                    high or low, a candle is considered an extreme
    To perform linear regression well (meaning draw a clear trendline) 
    more than once on one chart, I need to be able to assign starting points
    and end points to the lines.

    Starting points brainstorm:
    -- higher highs / lower highs (easiest)
    This function will find local extrema that will act as starting points

    returns:
        extrema_only
    '''
    # TODO make less if statements
    # TODO -> save highs and lows to dataframe 
    # concerns -> 1. what if i want several distance columns
    #             2. what if i want to update high/lows columns
    def identify_lows_highs(self, ohlc, extrema_type, distance):

        # if too short, don't consider it
        if len(ohlc) <= distance * 4:
            return pd.DataFrame()

        if extrema_type == "h" or extrema_type == "high":
            extrema_type = "h"
            isHigh = True
        elif extrema_type == "l" or extrema_type == "low":
            extrema_type == "l"
            isHigh = False
        else:
            raise ValueError("Wrong input for extrema_type parameter in identify_lows_highs()")

        ohlc[f"{extrema_type}_extremes_{distance}"] = True

        '''
        itertuples is much faster than iterrows cause of less type checking
        name=None refers to creating a pure tuple with no reference to columns
        in this case, I am not even using the tuple
        '''
        for i in range(len(ohlc)):
            # skip to avoid index out of bounds
            if i < distance * 2:
                continue
            # get earliest value of the distance specified
            earliest_index = i - distance
            earliest_price = ohlc.at[earliest_index, extrema_type]
            # get most extreme value in the range (either low or high)
            # compare if earliest is the most extreme in the range given
            # if not mark earliest given time as NOT the extreme
            if isHigh:
                most_extreme = ohlc.loc[i - distance * 2 : i, extrema_type].max()
            if not isHigh:
                most_extreme = ohlc.loc[i - distance * 2 : i, extrema_type].min()

            # compare if earlist is the most extreme in the range given
            if earliest_price < most_extreme and isHigh:
                ohlc.at[i - distance, f"{extrema_type}_extremes_{distance}"] = False
            if earliest_price > most_extreme and not isHigh:
                ohlc.at[i - distance, f"{extrema_type}_extremes_{distance}"] = False
        
        # the ends of the period are not reliable, due to the lack of data
        ohlc.at[:distance*2, f"{extrema_type}_extremes_{distance}"] = False
        ohlc.at[len(ohlc)-distance:, f"{extrema_type}_extremes_{distance}"] = False

        extrema_only = ohlc[ohlc[f"{extrema_type}_extremes_{distance}"]==True]
        return extrema_only

    '''
    params:
        distance -> number of candles passed after which, if price fails to make a new extreme 
                    high or low, a candle is considered an extreme

    usually you are gonna want to get both highs and lows for a given stock.
    thus this function calls identify_lows_highs with both params low and the high, keeping the same
    distance and concatanating the two together.

    returns:
        both_high_low_df -> either empty Dataframe if nothing to append or new highs/lows DF

    '''
    def identify_both_lows_highs(self, distance):
        highs_stock_df = self.identify_lows_highs(extrema_type="h", distance=distance)
        lows_stock_df = self.identify_lows_highs(extrema_type="l", distance=distance)

        if len(highs_stock_df) == 0 and len(lows_stock_df) == 0:
            return pd.DataFrame()
        # process concatanation
        both_high_low_df = pd.concat([highs_stock_df, lows_stock_df])
        both_high_low_df.fillna(False, inplace=True)
        # heapsort cause "t" always has same num digits get ticker name to save data
        both_high_low_df.sort_values("t", inplace=True, kind="heapsort") 
        return both_high_low_df

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
    def get_higher_extrema(self, extrema_df, extrema, distance, above_last_num_highs):
        # get all highs only
        highs_df = extrema_df[extrema_df[f"{extrema}_extremes_{distance}"]==True]
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

