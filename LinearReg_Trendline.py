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


    print(ohlc_data['low_trend'].head())

    ohlc_data['Adj Close'].plot()
    ohlc_data['high_trend'].plot()
    ohlc_data['low_trend'].plot()
    plt.show()

    return ohlc_data


