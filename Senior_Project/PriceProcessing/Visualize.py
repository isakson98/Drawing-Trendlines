# using libraries for visualizations
import plotly.graph_objects as go
import matplotlib.pyplot as plt # for trendlines

# visualizing price and additional components if necessary
def visualize_ticker(ohlc_data, additional_stuff):

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
    fig.update_yaxes(fixedrange = False)
    ohlc_data["Close"].plot(figsize=(15, 8))
    for i, r in additional_stuff.iterrows():
        fig.add_trace(go.Scatter(x=[r["points"][0][0], r["points"][-1][0]],
                                 y=[r["points"][0][1], r["points"][-1][1]],
                                 mode="lines",
                                 line=go.scatter.Line(color="black"),
                                 showlegend=False))

    fig.show()