import pandas as pd


'''

This class is going to have methods to process raw data given 
to develop features



'''
class TickerProcessing:

    ohlc = pd.DataFrame()

    def __init__(self, ohlc):
        self.ohlc = ohlc

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
    '''
    # TODO make less if statements
    # TODO -> save highs and lows to dataframe 
    # concerns -> 1. what if i want several distance columns
    #             2. what if i want to update high/lows columns
    def identify_lows_highs(self, extrema_type, distance):

        # if too short, don't consider it
        if len(self.ohlc) <= distance * 4:
            return pd.DataFrame()

        if extrema_type == "h" or extrema_type == "high":
            extrema_type = "h"
            isHigh = True
        elif extrema_type == "l" or extrema_type == "low":
            extrema_type == "l"
            isHigh = False
        else:
            raise ValueError("Wrong input for extrema_type parameter in identify_lows_highs()")

        self.ohlc[f"{extrema_type}_extremes_{distance}"] = True

        for i, r in self.ohlc.iterrows():
            # skip to avoid index out of bounds
            if i < distance * 2:
                continue
            # get earliest value of the distance specified
            earliest_index = i - distance
            earliest_price = self.ohlc.at[earliest_index, extrema_type]
            # get most extreme value in the range (either low or high)
            # compare if earliest is the most extreme in the range given
            # if not mark earliest given time as NOT the extreme
            if isHigh:
                most_extreme = self.ohlc.loc[i - distance * 2 : i, extrema_type].max()
            if not isHigh:
                most_extreme = self.ohlc.loc[i - distance * 2 : i, extrema_type].min()

            # compare if earlist is the most extreme in the range given
            if earliest_price < most_extreme and isHigh:
                self.ohlc.at[i - distance, f"{extrema_type}_extremes_{distance}"] = False
            if earliest_price > most_extreme and not isHigh:
                self.ohlc.at[i - distance, f"{extrema_type}_extremes_{distance}"] = False
        
        self.ohlc.at[:distance*2, f"{extrema_type}_extremes_{distance}"] = False

        extrema_only = self.ohlc[self.ohlc[f"{extrema_type}_extremes_{distance}"]==True]
        return extrema_only

    '''
    params:
        prev_high_low_file -> data from the last high/low file
    
    retrieving currently saved high/low file for the particular stock to find the last low/high available
    and update all of them

    '''
    def update_highs_lows(self, prev_high_low_file):

        # parse out parameters from the name columns
        
        # cut out properly the raw data, so you can start from the end

        # 
        pass
