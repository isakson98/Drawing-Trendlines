# using to access file
import pandas as pd

# calculating trendlines
from scipy.stats import linregress

'''

This class is responsible for drawing trendlines 

There is a lot of variability in how to draw a trendline,
and I am going to do my best to allow for that.

ex. where to start a trendline, where to end a trendline,
    which attribute to draw a column on (highs, lows, vwap),
    length of trendline, 

TIMEFRAME AGNOSTIC -> only price matters 

the job of this class is to not only calculate trendlines
but do it efficiently and report these trendlines in such
a way that it is conveninient to use this data later on.

'''
class TrendlineDrawing:

    raw_ohlc = pd.DataFrame()
    breakout_based_on = None
    trendline_cache = {}

    '''
    params:
        ohlc_raw -> raw data from Polygon API
        start_points_list -> list of ohlc_raw's indices where to start drawing trendlines from
        breakout_based_on -> allows to specify the criteria for a breakout (programmable)
                            allowed values so far "close" and 

    purpose: 
        At this momement in time, to draw a trendline, I need two things:
        the raw data and the starting points of each trendline in advance
        before starting this class

        Since, I have these two pieces of info in different locations,
        I need to merge the two together to make to perform calculations in this class

        IMPORTANT : ohlc_raw and starting_extrema_series must have the same index

    '''
    def __init__(self, ohlc_raw, start_points_list, breakout_based_on):
        self.raw_ohlc = ohlc_raw
        self.breakout_based_on = breakout_based_on
        self.start_points_list = start_points_list

    '''
    params:
        series_strip -> strip from extrema till the end of the given consolidation
        hash_key_parts -> list, elements of which form the key in a consecutive order
                          [starting time stamp, candles forward, length of series, unit drawn on]
    
    purpose: 
        In order to avoid calculating the same linear regression line on the same strip of series,
        I decided to calculate it only once and cache the result for future use.

        I am caching the trendline by constructing a special key, that should identify the line it should calculate

        This will require quite a bit more memory overhead, but from my analysis it could 2x the trendline identificaiton speed

    return:
        list [series -> strip of data shortened as a result of linear regression, reg -> values about the trendline]
    
    '''
    def __locate_trendline(self, series_strip, hash_key_parts):
        # create the hash key
        hash_key_parts[0] = int(hash_key_parts[0] / 100000) # convert ms to seconds to avoid longer hash keys
        string_parts = [str(element) for element in hash_key_parts]
        trendline_cache_key = ''.join(string_parts)
        # verify if this series strip has already been calculated
        if trendline_cache_key in self.trendline_cache:
            series_strip, reg = self.trendline_cache[trendline_cache_key]
        else:
            line_unit_col = hash_key_parts[-1] # always the last part 
            # calculate linear regression on a slice of days after the starting point
            series_strip, reg = self.__calculate_lin_reg(series_strip, line_unit_col)
            # save the new 
            self.trendline_cache[trendline_cache_key] = [series_strip, reg]

        return series_strip, reg


    '''
    params: 
        series_strip -> y values of the linear regression
        extreme -> either "h" or "l" : whether to filter values that are above the line or below

    purpose: 
        calculate_lin_reg() accomodates finding both
        ascending and descending trendlines

        ENSURE that the index values are in linear consecutive ascending order (not random 45,71,43)

        this function eliminates values that are either below or above the linear regression, thus,
        smoothing out the trendline based on the extremas within the consolidation.

    return:
        list[series -> strip of data after linear regression applied, reg -> linear regerssion object with slope values, etc]

    '''
    def __calculate_lin_reg(self, series_strip, extreme):
        reg = linregress(x=series_strip.index,y=series_strip)
        if extreme == "h":
            data1 = series_strip.loc[series_strip > reg[0] * series_strip.index + reg[1] ]
        elif extreme == "l":
            data1 = series_strip.loc[series_strip < reg[0] * series_strip.index + reg[1] ]

        return data1, reg


    '''
    params:
        line_unit_col -> name of columns the linear regression will be drawn on
                         like : "h", "low", etc -> make sure they are calculated ahead of time (if needed)
        start -> determining where to start the process of looking for trendline
        end -> determining where to end the process of looking for trendline
        min_days_out -> how many days to pass to start drawing a trendline
        preciseness -> how many "touches" do you your trendline to have
        max_trendlines_drawn -> maximum trendlines drawn from one starting position

    purpose: 
        allows to specify which range of values you want a trendline to be drawn at
        calculating trendlines based on the price candles

        with a start point identified, we need to identify the end
        in a primitive approach -> iterate by each day (starting from +5 days)
        until a new candles high is above the linear regression from yesterdays

        precisesness -> the higher the number, the more candles algo will draw the line over

    return: 
        df, where each row is a new trendline

    '''
    # TODO compartmentalize to accomodate which section to build a trendline on
    def identify_trendlines(self, line_unit_col, preciseness, start=None, end=None, min_days_out=5, max_trendlines_drawn=2):

        # if a start date is not given, assume the entire chart for a trendline 
        if start != None:
            self.raw_ohlc = self.raw_ohlc[start:end]

        row_list = []
        # find trendlines from each local extrema
        for local_extreme in self.start_points_list:
            # initialize values
            trendline_count = 0
            days_forward = min_days_out
            end_index = None 
            crossed_trendline = False
            # iterate from the same local extrema each day until the end of data or length is too big
            while local_extreme + days_forward < self.raw_ohlc.index[-1] - 1 and days_forward <= 42 and trendline_count < max_trendlines_drawn: # 42 is 2 month period -> max for my preference
                end_index = local_extreme + days_forward
                # retrieving only piece of series, which will be calculated on
                series_strip = self.raw_ohlc[line_unit_col].loc[local_extreme:end_index].copy() # end is included
                prev_data_len = 100 # anything more than 42 is ok (whats greater than days_forward) to init this var
                # draw the trendline through linear regression
                # have to figure out when to identify a breakout from the trendline
                while len(series_strip) > preciseness and trendline_count < max_trendlines_drawn and len(series_strip) != prev_data_len:
                    # keeping track of prev allows to mitigate stuck up values
                    prev_data_len = len(series_strip)
                    hash_key_parts = [self.raw_ohlc.at[local_extreme, "t"], days_forward, prev_data_len, line_unit_col]
                    series_strip, reg = self.__locate_trendline(series_strip, hash_key_parts)
                    # do not check trendlines until we have cut enough of data in the series strip
                    if len(series_strip) != preciseness:
                        continue

                    # get price at which trendline would be on the next day, the day it could breakout 
                    index_of_breakout_day = end_index + 1
                    trendline_price_last_day = round(reg[0] * (index_of_breakout_day) + reg[1], 2)
                    it_really_did = self.breakout_happend(trendline_price_last_day, 
                                                          local_extreme, 
                                                          index_of_breakout_day, 
                                                          line_unit_col)

                    # theres no breakout, iterate through breakout, without counting each next day as a trendline breakout
                    # wait the breakout passed, so you can start counting a new breakout from the same starting local extrema
                    if it_really_did and crossed_trendline == False:
                        # save trendline
                        row_dict = {"t_start":self.raw_ohlc.at[local_extreme, "t"] , 
                                    "t_end":self.raw_ohlc.at[index_of_breakout_day, "t"], 
                                    "price_start":self.raw_ohlc.loc[local_extreme,line_unit_col], 
                                    "price_end":trendline_price_last_day,
                                    "slope" : reg[0], "intercept" : reg[1], "rvalue" : reg[2], "pvalue" : reg[3],
                                    "base_length" : days_forward + 1,
                                    "preciseness" : preciseness}
                        row_list.append(row_dict)
                        trendline_count += 1
                        crossed_trendline = True
                    # BOTH MUST BE PRESENT TO REACTIVATE TRENDLINE COUNTING
                    elif not it_really_did and crossed_trendline == True:
                        crossed_trendline = False
                
                days_forward += 1
            
        trendlines_df = pd.DataFrame(row_list)
        return trendlines_df

    '''
    params:
        trendline_pos_bo_day -> the price of trendline at the breakout day
        local_extreme_index -> index of the starting point of the trendline on the total dataframe
        index_of_breakout_day -> index of breakout on the total dataframe
        extrema_type -> what the lin reg is calculated on

    purpose: 
        this function has options for how to determine a breakout. It is UPDATEABLE,
        meaning a user can modify when he considers a breakout to have occured.

        Insert new versions as if statements, name this version appropriately, and
        add it to a constructor

    returns:   
        boolean -> True if breakout occured / False if not
    
    '''
    # TODO : think whether I want to separate logic where user gets involved and the engine is,
    #  so a user does not think he can change the logic in the engine, too.
    def breakout_happend(self, trendline_pos_bo_day, local_extreme_index, index_of_breakout_day, extrema_type):
        # get the half of standard deviation in the period of the range
        roll_std = self.raw_ohlc.loc[local_extreme_index:index_of_breakout_day-1, extrema_type].std() / 2

        # shortened variable names. bo => breakout
        up_pivot_price  = trendline_pos_bo_day + roll_std
        down_pivot_price  = trendline_pos_bo_day - roll_std 
        bo_day_open = self.raw_ohlc.loc[index_of_breakout_day,"o"] 
        bo_day_high = self.raw_ohlc.loc[index_of_breakout_day,"h"] 
        bo_day_low = self.raw_ohlc.loc[index_of_breakout_day,"l"]
        bo_day_close = self.raw_ohlc.loc[index_of_breakout_day,"c"]

        # simply close above/below pivot point
        if self.breakout_based_on == "any close":
            # using breakouts's day close as the pivot point
            if up_pivot_price < bo_day_close and  extrema_type =="h":
                return True
            elif down_pivot_price > bo_day_close and extrema_type =="l":
                return True
            else:
                return False

        # closed above/below pivot point AND green/red in the proper direction
        elif self.breakout_based_on == "strong close":
            # using breakouts's day close as the pivot point
            if up_pivot_price < bo_day_close and bo_day_close > bo_day_open and extrema_type =="h":
                return True
            elif down_pivot_price > bo_day_close and bo_day_open > bo_day_close and  extrema_type =="l":
                return True
            else:
                return False

        # based on the stock crossing the price of the pivot on the day. doesn't matter if happened once and closed weak
        elif self.breakout_based_on == "initial spike":
            # using breakouts's day close as the pivot point
            if up_pivot_price < bo_day_high and extrema_type =="h":
                return True
            elif down_pivot_price > bo_day_low and extrema_type =="l":
                return True
            else:
                return False

    '''
    params:
        none
    
    purpose:
        To avoid keys hitting the content of the previous trendline, i clear the dictionary
        after having completed drawing the trendlines

    return:
        none

    '''
    def clear_cache(self):
        self.trendline_cache.clear()
