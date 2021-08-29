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

    '''
    params:
        ohlc_raw -> raw data from Polygon API
        extrema_df -> processed highs and lows (with Polygons API columns)
        breakout_based_on -> allows to specify the criteria for a breakout (programmable)
                            allowed values so far "close" and 

    At this momement in time, to draw a trendline, I need two things:
    the raw data and the starting points of each trendline in advance
    before starting this class

    Since, I have these two pieces of info in different locations,
    I need to merge the two together to make to perform calculations in this class

    '''
    def __init__(self, ohlc_raw, starting_extrema_df, breakout_based_on):
        self.raw_ohlc = ohlc_raw
        self.breakout_based_on = breakout_based_on
        self.starting_extrema_df = starting_extrema_df


    '''
    calculate_lin_reg() accomodates finding both
    ascending and descending trendlines
    '''
    def __calculate_lin_reg(self, ohlc_portion, x_index, y_prices, extreme):
        reg = linregress(x=x_index,y=y_prices)
        if extreme == "h":
            data1 = ohlc_portion.loc[y_prices > reg[0] * x_index + reg[1] ]
        elif extreme == "l":
            data1 = ohlc_portion.loc[y_prices < reg[0] * x_index + reg[1] ]

        return data1, reg


    '''
    params:
        distance -> starting extrema's parameter
        extrema_type -> starting price of the trendline ("h", "low", etc) -> 
                        make sure they are calculated ahead of time
        start -> determining where to start the process of looking for trendline
        end -> determining where to end the process of looking for trendline
        min_days_out -> how many days to pass to start drawing a trendline
        preciseness -> how many "touches" do you your trendline to have
        max_trendlines_drawn -> maximum trendlines drawn from one starting position

    allows to specify which range of values you want a trendline to be drawn at
    calculating trendlines based on the price candles

    with a start point identified, we need to identify the end
    in a primitive approach -> iterate by each day (starting from +5 days)
    until a new candles high is above the linear regression from yesterdays

    precisesness -> the higher the number, the more candles algo will draw the line over

    '''
    # TODO compartmentalize to accomodate which section to build a trendline on
    def identify_trendlines_LinReg(self, distance, extrema_type, precisesness, start=None, end=None, min_days_out=5, max_trendlines_drawn=3):

        # if a start date is not given, assume the entire chart for a trendline 
        if start != None:
            self.raw_ohlc = self.raw_ohlc[start:end]

        # retrieve index values where high extremes are
        extreme_points  = self.starting_extrema_df[self.starting_extrema_df[f"{extrema_type}_extremes_{distance}"]==True].index.tolist()
        row_list = []
        row_dict = {"t_start":0, "t_end":0, "price_start":0, "price_end":0}
        printed=False
        # find trendlines from each local extrema
        for index, local_extreme in enumerate(extreme_points):
            # keep track of progress
            progress = int(round(index / len(extreme_points) * 100, -1))
            if progress % 20 == 0 and not printed:
                print(f"{progress}% done")
                printed = True
            elif progress % 20 != 0:
                printed = False

            # initialize values
            timestamp_local_extreme = self.raw_ohlc.at[local_extreme, "t"]
            trendline_count = 0
            days_forward = min_days_out
            end_index = None 
            crossed_trendline = False

            # iterate each day until the end of data or length is too big
            while local_extreme + days_forward < self.raw_ohlc.index[-1] - 1 and days_forward <= 42: # 42 is 2 month period -> max for my preference
                end_index = local_extreme + days_forward
                data1 = self.raw_ohlc.loc[local_extreme:end_index,:].copy() # end is included
                prev_data_len = 100 # anything more than 42 is ok (whats greater than days_forward) to init this var
                # draw the trendline through linear regression
                # have to figure out when to identify a breakout from the trendline
                while len(data1) > precisesness and trendline_count < max_trendlines_drawn and len(data1) != prev_data_len:
                    # keeping track of prev allows to mitigate stuck up values
                    prev_data_len = len(data1)
                    # calculate linear regression on a slice of days after the starting point
                    data1, reg = self.__calculate_lin_reg(data1, data1.index, data1[extrema_type], extrema_type)

                    # do not check trendlines until we have cut enough of data
                    if len(data1) != precisesness:
                        continue

                    # get price at which trendline would be on the next day, the day it could breakout 
                    index_of_breakout_day = end_index + 1
                    trendline_price_last_day = reg[0] * (index_of_breakout_day) + reg[1] 
                    it_really_did = self.breakout_happend(trendline_price_last_day, 
                                                          local_extreme, 
                                                          index_of_breakout_day, 
                                                          extrema_type)

                    # theres no breakout, iterate through breakout, without counting each next day as a trendline breakout
                    # wait the breakout passed, so you can start counting a new breakout from the same starting local extrema
                    if it_really_did and crossed_trendline == False:
                        # gather data to pass to a function which will determine if a breakout happened
                        trendline_start_price = self.raw_ohlc.loc[local_extreme,extrema_type]
                        # get the timestamp of the day 
                        timestamp_end_trend = self.raw_ohlc.at[index_of_breakout_day, "t"]
                        # save trendline
                        row_dict = {"t_start":timestamp_local_extreme, 
                                    "t_end":timestamp_end_trend, 
                                    "price_start":trendline_start_price, 
                                    "price_end":trendline_price_last_day}
                        row_list.append(row_dict)
                        # trendline upkeeping
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
        trendlines_df -> dataframe straight from self.identify_trendlines_LinReg()

    remove trendlines where the end price of the trendline is higher than origin.
    
    Decided to have this function outside of the main trendline drawing function 
    to avoid clustering too many things in it.

    returns:
        descending_df -> same columns 
    '''
    def remove_ascending_trendlines(self, trendlines_df):

        if "price_start" not in trendlines_df.columns:
            print('''Cannot remove trendlines. There is "price_start" column in trendlines_df''')
            return trendlines_df
        
        descending_df = trendlines_df[(trendlines_df["price_start"] > trendlines_df["price_end"] )]

        return descending_df
    
    '''
    params:
        trendlines_df -> dataframe straight from self.identify_trendlines_LinReg()

    remove trendlines where the end price of the trendline is higher than origin

    returns:
        ascending_df -> same columns 
    '''
    def remove_descending_trendlines(self, trendlines_df):

        if "price_start" not in trendlines_df.columns:
            print('''Cannot remove trendlines. There is "price_start" column in trendlines_df''')
            return trendlines_df

        ascending_df = trendlines_df[(trendlines_df["price_start"] < trendlines_df["price_end"] )]
         
        return ascending_df