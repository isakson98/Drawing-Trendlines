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



class Trendline_Drawing:

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

        if ohlc_type == "High":
            isHigh = True
        else:
            isHigh = False


        self.ohlc[f"{ohlc_type} Extremes"] = True

        for i, r in self.ohlc.iterrows():
            # skip to avoid index out of bounds
            if i < distance * 2:
                continue
            # get earliest value
            earliest = self.ohlc.at[i - distance, ohlc_type]
            # get most extreme value in the range (either low or high)
            if isHigh:
                most_extreme = self.ohlc.loc[i - distance * 2 : i, ohlc_type].max()
            if not isHigh:
                most_extreme = self.ohlc.loc[i - distance * 2 : i, ohlc_type].min()

            # compare if earlist is the most extreme in the range given
            if earliest < most_extreme and isHigh:
                self.ohlc.at[i - distance, f"{ohlc_type} Extremes"] = False
            if earliest > most_extreme and not isHigh:
                self.ohlc.at[i - distance, f"{ohlc_type} Extremes"] = False
        
        self.ohlc.at[:distance*2, f"{ohlc_type} Extremes"] = False

        return self.ohlc

    '''
    calculate_lin_reg() accomodates finding both
    ascending and descending trendlines
    '''
    def calculate_lin_reg(self, ohlc_portion, x_index, y_prices, extreme):
        reg = linregress(x=x_index,y=y_prices)
        if extreme == "High":
            data1 = ohlc_portion.loc[y_prices > reg[0] * x_index + reg[1] ]
        elif extreme == "Low":
            data1 = ohlc_portion.loc[y_prices < reg[0] * x_index + reg[1] ]

        return data1, reg


    '''
    allows to specify which range of values you want a trendline to be drawn at
    calculating trendlines based on the price candles

    with a start point identified, we need to identify the end
    in a primitive approach -> iterate by each day (starting from +5 days)
    until a new candles high is above the linear regression from yesterdays

    precisesness -> the higher the number, the more candles algo will draw the line over

    '''
    # TODO merge ascending and descending trendline into if possible
    def identify_trendlines_LinReg(self, start=None, end=None, extreme="High", min_days_out=5, precisesness=4, max_trendlines_drawn=3):

        extreme = extreme.lower().capitalize()

        # if a start date is not given, assume the entire chart for a trendline 
        if start != None:
            self.ohlc = self.ohlc[start:end]

        # retrieve index values where high extremes are
        extreme_points  = self.ohlc[self.ohlc[f"{extreme} Extremes"]==True].index.tolist()
        trendlines_start_end_points = []

        # find trendlines from each high
        for local_extreme in extreme_points:
            trendline_count = 0
            days_forward = min_days_out
            end_index = local_extreme # I count trendlines at least of 5 days
            crossed_trendline = False
            # iterate though each day forward to find several trendlines from same high
            while end_index + days_forward + 1 < self.ohlc.index[-1] :
                end_index = local_extreme + days_forward
                data1 = self.ohlc.loc[local_extreme:end_index,:].copy()
                # draw the trendline through linear regression
                # have to figure out when to identify a breakout from the trendline
                while len(data1) > precisesness and trendline_count < max_trendlines_drawn: #TODO -> fix hyperparameter number 2

                    #  slope, intercept, r, p, se = linregress(x, y)
                    data1, reg = self.calculate_lin_reg(data1, data1.index, data1[extreme], extreme)

                    # do not check trendlines until we have cut enough of data
                    if len(data1) != precisesness:
                        continue

                    # if current high is above computed trendline that ends on previous candle ->
                    # this is a break out
                    roll_std = data1.loc[end_index - min_days_out:end_index, extreme].std() / 2
                    trendline_start_price = self.ohlc.loc[local_extreme,extreme] 
                    trendline_pos_new_day = reg[0] * (end_index + 1) + reg[1] 


                    if trendline_pos_new_day + roll_std < self.ohlc.loc[end_index + 1,extreme] and extreme =="High" and crossed_trendline == False:
                        current_start_endpoints = [(local_extreme, trendline_start_price),
                                                    (end_index + 1, trendline_pos_new_day)]
                        trendlines_start_end_points.append(current_start_endpoints)
                        trendline_count += 1
                        crossed_trendline = True

                    elif trendline_pos_new_day - roll_std > self.ohlc.loc[end_index + 1,extreme] and extreme =="Low" and crossed_trendline == False:
                        current_start_endpoints = [(local_extreme, trendline_start_price),
                                                    (end_index + 1, trendline_pos_new_day)]
                        trendlines_start_end_points.append(current_start_endpoints)
                        trendline_count += 1
                        crossed_trendline = True
                    # theres no breakout
                    elif trendline_pos_new_day > self.ohlc.loc[end_index + 1,extreme] and extreme =="High" and crossed_trendline == True:
                        crossed_trendline = False

                    elif trendline_pos_new_day < self.ohlc.loc[end_index + 1,extreme] and extreme =="Low" and crossed_trendline == True:
                        crossed_trendline = False
                
                days_forward += 1

        technicals_df = pd.DataFrame({"points":trendlines_start_end_points})

        return technicals_df

