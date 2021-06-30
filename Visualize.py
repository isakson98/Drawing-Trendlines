# using libraries for visualizations
import plotly.graph_objects as go
import matplotlib.pyplot as plt # for trendlines

# visualizing price and additional components if necessary
def visualize_ticker(ohlc_data):

    price_trace = {
        'x': ohlc_data.index,
        'open': ohlc_data.Open,
        'close': ohlc_data.Close,
        'high': ohlc_data.High,
        'low': ohlc_data.Low,
        'type': 'candlestick',
        'showlegend': True
    }
    
    all_data = [price_trace]
    fig = go.Figure(all_data)
    fig.show()