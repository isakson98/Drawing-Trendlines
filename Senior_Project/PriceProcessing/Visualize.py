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
def visualize_ticker(all_ohlc_data, peaks_df:pd.DataFrame(), trendlines=pd.DataFrame(), distance=5, from_=None, to=None,):

    price_trace = {
        'x': all_ohlc_data.t,
        'open': all_ohlc_data.o,
        'close': all_ohlc_data.c,
        'high': all_ohlc_data.h,
        'low': all_ohlc_data.l,
        'type': 'candlestick',
        'showlegend': True
    }

    all_data = [go.Candlestick(price_trace)]

    if len(peaks_df) > 0:

        peaks_trace = {
            'x': peaks_df.t,
            'open': peaks_df.o,
            'close': peaks_df.c,
            'high': peaks_df.h,
            'low': peaks_df.l,
            'type': 'candlestick',
            'showlegend': True,
            'increasing' : {'line' : {'color':'purple'}},
            'decreasing' : {'line' : {'color':'purple'}},
        }
        # all_data = all_data.append(go.Candlestick(peaks_trace))

    all_data = [go.Candlestick(price_trace), go.Candlestick(peaks_trace)]
    fig = go.Figure(data = all_data)
    fig.update_yaxes(fixedrange = False)

    for row in trendlines.itertuples():
        fig.add_trace(go.Scatter(x=[row.t_start, row.t_end],
                                 y=[row.price_start, row.price_end],
                                 mode="lines",
                                 line=go.scatter.Line(color="black"),
                                 showlegend=False))

    fig.show()