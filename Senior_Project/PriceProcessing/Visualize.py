# using libraries for visualizations
from numpy import NaN
import plotly.graph_objs as go
import matplotlib.pyplot as plt # for trendlines
import pandas as pd


'''
params:
    ohlc_data -> raw price data 
    peaks -> straight up DataFrame from identify_both_lows_highs()
    trendlines -> straight up DataFrame from identify_trendlines_LinReg()


This function is used for visualizing purposes. it is used to examine whether what you want 
actually shows itself.

It adds different colors to what exactly you are checking for (purple for extrema, for instance)


'''
def visualize_ticker(ohlc_data, peaks=pd.DataFrame(), trendlines=pd.DataFrame()):

    price_trace = {
        'x': ohlc_data.t,
        'open': ohlc_data.o,
        'close': ohlc_data.c,
        'high': ohlc_data.h,
        'low': ohlc_data.l,
        'type': 'candlestick',
        'showlegend': True
    }

    peaks_trace = {
        'x': peaks.t,
        'open': peaks.o,
        'close': peaks.c,
        'high': peaks.h,
        'low': peaks.l,
        'type': 'candlestick',
        'showlegend': True,
        'increasing' : {'line' : {'color':'purple'}},
        'decreasing' : {'line' : {'color':'purple'}},
    }

    all_data = [go.Candlestick(price_trace), go.Candlestick(peaks_trace)]
    fig = go.Figure(data = all_data)
    fig.update_yaxes(fixedrange = False)

    for i, r in trendlines.iterrows():
        fig.add_trace(go.Scatter(x=[r["points"][0][0], r["points"][-1][0]],
                                 y=[r["points"][0][1], r["points"][-1][1]],
                                 mode="lines",
                                 line=go.scatter.Line(color="black"),
                                 showlegend=False))

    fig.show()