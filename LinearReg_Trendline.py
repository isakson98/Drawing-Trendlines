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

# to perform linear regression well (meaning draw a clear trendline) 
# more than once on one chart, I need to be able to assign starting points
# and end points to the lines.
# Starting points brainstorm:
# -- higher highs / lower highs (easiest)
# -- 
def identify_lows_highs(ohlc, ohlc_type, len, isHigh):

    ohlc = ohlc.reset_index()
    ohlc[f"{ohlc_type} Extremes"] = True
    print(ohlc.head())

    for i, r in ohlc.iterrows():
        # skip to avoid index out of bounds
        if i < len * 2:
            continue
        # get earliest value
        earliest = ohlc.at[i - len, ohlc_type]
        # get most extreme value in the range (either low or high)
        if isHigh:
            most_extreme = ohlc.loc[i - len * 2 : i, ohlc_type].max()
        if not isHigh:
            most_extreme = ohlc.loc[i - len * 2 : i, ohlc_type].min()

        # compare if earlist is the most extreme in the range given
        if earliest < most_extreme and isHigh:
            ohlc.at[i - len, f"{ohlc_type} Extremes"] = False
        if earliest > most_extreme and not isHigh:
            ohlc.at[i - len, f"{ohlc_type} Extremes"] = False

        if ohlc.at[i - len , f"{ohlc_type} Extremes"]:
            print(ohlc.at[i - len , "Date"])

    return ohlc


# allows to specify which range of values you want a trendline to be drawn at
# calculating trendlines based on the price candles
# calculates one ascending and one descending trendline
def identify_trendlines_LinReg(ohlc_data, start=None, end=None):

    # if not default
    if start != None:
        ohlc_data = ohlc_data[start:end]

    ohlc_data['date_id'] = ((ohlc_data.index - ohlc_data.index.min())).astype('timedelta64[D]')
    ohlc_data['date_id'] = ohlc_data['date_id'] + 1

    # descending trend line
    data1 = ohlc_data.copy()
    while len(data1)>2:
        # slope, intercept, r, p, se = linregress(x, y)
        reg = linregress(
                        x=data1['date_id'],
                        y=data1['High'],
                        )

        data1 = data1.loc[data1['High'] > reg[0] * data1['date_id'] + reg[1]]
 
        ohlc_data['high_trend'] = reg[0] * ohlc_data['date_id'] + reg[1]


    # ascending trend line
    data1 = ohlc_data.copy()
    while len(data1)>2:
        reg = linregress(
                        x=data1['date_id'],
                        y=data1['Low'],
                        )
        # removes all prices point that are above the ascending trendline
        data1 = data1.loc[data1['Low'] < reg[0] * data1['date_id'] + reg[1]]
        ohlc_data['low_trend'] = reg[0] * ohlc_data['date_id'] + reg[1]


    first_date = ohlc_data.index[0]
    last_date = ohlc_data.index[-1]

    high_trend = [(first_date, ohlc_data.at[first_date, 'high_trend']),
                 (last_date, ohlc_data.at[last_date, 'high_trend'])]
    
    low_trend = [(first_date, ohlc_data.at[first_date, 'low_trend']),
                 (last_date, ohlc_data.at[last_date, 'low_trend'])]

    technicals_df = pd.DataFrame({"points":[high_trend, low_trend]})

    return ohlc_data, technicals_df


