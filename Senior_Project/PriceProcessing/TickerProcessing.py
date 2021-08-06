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
    To perform linear regression well (meaning draw a clear trendline) 
    more than once on one chart, I need to be able to assign starting points
    and end points to the lines.

    Starting points brainstorm:
    -- higher highs / lower highs (easiest)
    This function will find local extrema that will act as starting points
    '''
    # TODO make less if statements
    # TODO -> save highs and lows to dataframe 
    def identify_lows_highs(self, ohlc_type, distance=5):

        if ohlc_type == "h":
            isHigh = True
        elif ohlc_type == "l":
            isHigh = False
        else:
            raise ValueError("Wrong input for ohlc_type parameter in identify_lows_highs()")

        self.ohlc[f"{ohlc_type} Extremes"] = True

        for i, r in self.ohlc.iterrows():
            # skip to avoid index out of bounds
            if i < distance * 2:
                continue
            # get earliest value of the distance specified
            earliest_index = i - distance
            earliest_price = self.ohlc.at[earliest_index, ohlc_type]
            # get most extreme value in the range (either low or high)
            # compare if earliest is the most extreme in the range given
            # if not mark earliest given time as NOT the extreme
            if isHigh:
                most_extreme = self.ohlc.loc[i - distance * 2 : i, ohlc_type].max()
            if not isHigh:
                most_extreme = self.ohlc.loc[i - distance * 2 : i, ohlc_type].min()

            # compare if earlist is the most extreme in the range given
            if earliest_price < most_extreme and isHigh:
                self.ohlc.at[i - distance, f"{ohlc_type} Extremes"] = False
            if earliest_price > most_extreme and not isHigh:
                self.ohlc.at[i - distance, f"{ohlc_type} Extremes"] = False
        
        self.ohlc.at[:distance*2, f"{ohlc_type} Extremes"] = False


        return self.ohlc

    pass