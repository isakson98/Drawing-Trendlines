# using libraries for visualizations
import matplotlib.pyplot as plt

# using to access file
import pandas as pd
import os

# calculating trendlines
from scipy.stats import linregress
import datetime as dt

# data extraction
from DataExtract import retrieve_ticker_data
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
def identify_lows_highs(ohlc, ohlc_type, distance=5):

    if ohlc_type == "High":
        isHigh = True
    else:
        isHigh = False


    ohlc[f"{ohlc_type} Extremes"] = True

    for i, r in ohlc.iterrows():
        # skip to avoid index out of bounds
        if i < distance * 2:
            continue
        # get earliest value
        earliest = ohlc.at[i - distance, ohlc_type]
        # get most extreme value in the range (either low or high)
        if isHigh:
            most_extreme = ohlc.loc[i - distance * 2 : i, ohlc_type].max()
        if not isHigh:
            most_extreme = ohlc.loc[i - distance * 2 : i, ohlc_type].min()

        # compare if earlist is the most extreme in the range given
        if earliest < most_extreme and isHigh:
            ohlc.at[i - distance, f"{ohlc_type} Extremes"] = False
        if earliest > most_extreme and not isHigh:
            ohlc.at[i - distance, f"{ohlc_type} Extremes"] = False

    return ohlc

'''
calculate_lin_reg() accomodates finding both
ascending and descending trendlines
'''
def calculate_lin_reg(ohlc, x_index, y_prices, extreme):
    reg = linregress(x=x_index,y=y_prices)
    if extreme == "High":
        data1 = ohlc.loc[y_prices > reg[0] * x_index + reg[1]]
    elif extreme == "Low":
        data1 = ohlc.loc[y_prices < reg[0] * x_index + reg[1]]

    return data1, reg


'''
allows to specify which range of values you want a trendline to be drawn at
calculating trendlines based on the price candles

with a start point identified, we need to identify the end
in a primitive approach -> iterate by each day (starting from +5 days)
until a new candles high is above the linear regression from yesterdays

'''
# TODO merge ascending and descending trendline into if possible
def identify_trendlines_LinReg(ohlc, start=None, end=None, extreme="High", min_days_out=5, precisesness=4):

    extreme = extreme.lower().capitalize()

    # if a start date is not given, assume the entire chart for a trendline 
    if start != None:
        ohlc = ohlc[start:end]

    # retrieve index values where high extremes are
    extreme_points  = ohlc[ohlc[f"{extreme} Extremes"]==True].index.tolist()
    trendlines_start_end_points = []
    # find trendlines from each high (first five are dummies)
    for local_extreme in extreme_points[5:]:
        trendline_count = 0
        days_forward = min_days_out
        end_index = local_extreme # I count trendlines at least of 5 days
        # iterate though each day forward to find several trendlines from same high
        while trendline_count < 3 and end_index + days_forward + 1 < ohlc.index[-1] :
            end_index = local_extreme + days_forward
            data1 = ohlc.loc[local_extreme:end_index,:].copy()
            # draw the trendline through linear regression
            # have to figure out when to identify a breakout from the trendline
            while len(data1) > precisesness: #TODO -> fix hyperparameter number 2
                # slope, intercept, r, p, se = linregress(x, y)
                data1, reg = calculate_lin_reg(data1, data1.index, data1[extreme], extreme)

                # if current high is above computed trendline that ends on previous candle ->
                # this is a break out
                trendline_start_price = reg[0] * local_extreme + reg[1]
                trendline_pos_new_day = reg[0] * (end_index + 1) + reg[1]

                if trendline_pos_new_day < ohlc.loc[end_index + 1,extreme] and extreme =="High":
                    current_start_endpoints = [(local_extreme, trendline_start_price),
                                                (end_index + 1, trendline_pos_new_day)]
                    trendlines_start_end_points.append(current_start_endpoints)
                    trendline_count += 1

                elif trendline_pos_new_day > ohlc.loc[end_index + 1,extreme] and extreme =="Low":
                    current_start_endpoints = [(local_extreme, trendline_start_price),
                                                (end_index + 1, trendline_pos_new_day)]
                    trendlines_start_end_points.append(current_start_endpoints)
                    trendline_count += 1
            
            days_forward += 1

    technicals_df = pd.DataFrame({"points":trendlines_start_end_points})

    return ohlc, technicals_df


    
# allows to specify which range of values you want a trendline to be drawn at
# calculating trendlines based on the price candles
# calculates one ascending and one descending trendline
def identify_ascending_trendlines_LinReg(ohlc, start=None, end=None):

    ohlc = ohlc.reset_index()

    # if not default
    if start != None:
        ohlc = ohlc[start:end]

    ohlc['date_id'] = ((ohlc.index - ohlc.index.min())).astype('timedelta64[D]')
    ohlc['date_id'] = ohlc['date_id'] + 1

    # ascending trend line
    data1 = ohlc.copy()
    while len(data1)>2:
        reg = linregress(
                        x=data1['date_id'],
                        y=data1['Low'],
                        )
        # removes all prices point that are above the ascending trendline
        data1 = data1.loc[data1['Low'] < reg[0] * data1['date_id'] + reg[1]]
        ohlc['low_trend'] = reg[0] * ohlc['date_id'] + reg[1]


    first_date = ohlc.index[0]
    last_date = ohlc.index[-1]
    
    low_trend = [(first_date, ohlc.at[first_date, 'low_trend']),
                 (last_date, ohlc.at[last_date, 'low_trend'])]

    return ohlc, low_trend





