# using libraries for visualizations
from threading import local
import matplotlib.pyplot as plt

# using to access file
import numpy as np
import pandas as pd
import os

# calculating trendlines
from scipy.stats import linregress
import datetime as dt

'''

This class is responsible for drawing trendlines 

There is a lot of variability in how to draw a trendline,
and I am going to do my best to allow for that.

ex. where to start a trendline, where to end a trendline,
    which attribute to draw a column on (highs, lows, vwap),
    length of trendline, 

the job of this class is to not only calculate trendlines
but do it efficiently and report these trendlines in such
a way that it is conveninient to use this data later on.

'''
class Trendline_Drawing:

    ohlc_all_df = pd.DataFrame()

    '''
    params:
        ohlc_raw -> raw data from Polygon API
        extrema_df -> processed highs and lows (with Polygons API columns)

    At this momement in time, to draw a trendline, I need two things:
    the raw data and the starting points of each trendline in advance
    before starting this class

    Since, I have these two pieces of info in different locations,
    I need to merge the two together to make to perform calculations in this class

    '''
    def __init__(self, ohlc_raw, extrema_df):
        # find same columns to merge on 
        ohlc_raw_cols = set(ohlc_raw.columns.tolist())
        same_cols = list(ohlc_raw_cols.intersection(extrema_df.columns.tolist()))
        # merge two dataframes
        total_df = pd.merge(left=ohlc_raw, right=extrema_df, how="left", on=same_cols)
        # replace NaNs with false
        total_df.fillna(False, inplace=True)
        self.ohlc_all_df = total_df


    '''
    calculate_lin_reg() accomodates finding both
    ascending and descending trendlines
    '''
    def calculate_lin_reg(self, ohlc_portion, x_index, y_prices, extreme):
        reg = linregress(x=x_index,y=y_prices)
        if extreme == "h":
            data1 = ohlc_portion.loc[y_prices > reg[0] * x_index + reg[1] ]
        elif extreme == "l":
            data1 = ohlc_portion.loc[y_prices < reg[0] * x_index + reg[1] ]

        return data1, reg


    '''
    params:
        extrema_df -> df containing 
        distance ->
        extrema_type ->
        start ->
        end ->
        min_days_out ->
        preciseness ->
        max_trendlines_drawn ->

    allows to specify which range of values you want a trendline to be drawn at
    calculating trendlines based on the price candles

    with a start point identified, we need to identify the end
    in a primitive approach -> iterate by each day (starting from +5 days)
    until a new candles high is above the linear regression from yesterdays

    precisesness -> the higher the number, the more candles algo will draw the line over

    '''
    # TODO compartmentalize to accomodate which section to build a trendline on
    # TODO merge ascending and descending trendline into if possible
    def identify_trendlines_LinReg(self, distance, extrema_type, start=None, end=None, min_days_out=5, precisesness=4, max_trendlines_drawn=3):

        # if a start date is not given, assume the entire chart for a trendline 
        if start != None:
            self.ohlc_all_df = self.ohlc_all_df[start:end]

        # retrieve index values where high extremes are
        extreme_points  = self.ohlc_all_df [self.ohlc_all_df [f"{extrema_type}_extremes_{distance}"]==True].index.tolist()
        trendlines_start_end_points = []

        # find trendlines from each high
        for index, local_extreme in enumerate(extreme_points):
            progress = round(index / len(extreme_points) * 100)
            if progress % 10 == 0 and progress != 0:
                print(f"{progress}% done")
            timestamp_local_extreme = self.ohlc_all_df.at[local_extreme, "t"]
            trendline_count = 0
            days_forward = min_days_out
            end_index = local_extreme # I count trendlines at least of 5 days
            crossed_trendline = False
            # iterate each day until the end of data or length is too big
            while local_extreme + days_forward < self.ohlc_all_df.index[-1] - 1 and days_forward <= 63: #121 is half a year
                end_index = local_extreme + days_forward
                data1 = self.ohlc_all_df.loc[local_extreme:end_index,:].copy()
                # draw the trendline through linear regression
                # have to figure out when to identify a breakout from the trendline
                while len(data1) > precisesness and trendline_count < max_trendlines_drawn: #TODO -> fix hyperparameter number 2

                    #  slope, intercept, r, p, se = linregress(x, y)
                    data1, reg = self.calculate_lin_reg(data1, data1.index, data1[extrema_type], extrema_type)

                    # do not check trendlines until we have cut enough of data
                    if len(data1) != precisesness:
                        continue

                    # if current high is above computed trendline that ends on previous candle ->
                    # this is a break out
                    roll_std = data1.loc[end_index - min_days_out:end_index, extrema_type].std() / 2
                    trendline_start_price = self.ohlc_all_df.loc[local_extreme,extrema_type] 
                    trendline_pos_new_day = reg[0] * (end_index + 1) + reg[1] 

                    timestamp_end_trend = self.ohlc_all_df.at[end_index + 1, "t"]
                   
                    
                    # using breakouts's day close as the pivot point
                    if trendline_pos_new_day + roll_std < self.ohlc_all_df.loc[end_index + 1,"c"] and extrema_type =="h" and crossed_trendline == False:
                        current_start_endpoints = [(timestamp_local_extreme, trendline_start_price),
                                                    (timestamp_end_trend, trendline_pos_new_day)]
                        trendlines_start_end_points.append(current_start_endpoints)
                        trendline_count += 1
                        crossed_trendline = True

                    elif trendline_pos_new_day - roll_std > self.ohlc_all_df.loc[end_index + 1,"c"] and extrema_type =="l" and crossed_trendline == False:
                        current_start_endpoints = [(timestamp_local_extreme, trendline_start_price),
                                                    (timestamp_end_trend, trendline_pos_new_day)]
                        trendlines_start_end_points.append(current_start_endpoints)
                        trendline_count += 1
                        crossed_trendline = True
                    # theres no breakout
                    elif trendline_pos_new_day > self.ohlc_all_df.loc[end_index + 1,extrema_type] and extrema_type =="h" and crossed_trendline == True:
                        crossed_trendline = False

                    elif trendline_pos_new_day < self.ohlc_all_df.loc[end_index + 1,extrema_type] and extrema_type =="l" and crossed_trendline == True:
                        crossed_trendline = False
                
                days_forward += 1

        technicals_df = pd.DataFrame({"points":trendlines_start_end_points})

        return technicals_df
