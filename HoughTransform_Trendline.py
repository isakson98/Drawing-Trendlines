# Background reading:
# http://www.meacse.org/ijcar/archives/128.pdf
# taken from this article:
# https://towardsdatascience.com/algorithmically-drawing-trend-lines-on-a-stock-chart-414ed66d0055
# using this library:
# https://github.com/KIC/pandas-ml-quant/blob/f9f92477a6d99443e5ee7966faabfa428265bdf6/pandas-ta-quant/pandas_ta_quant/technical_analysis/forecast/support.py

from sklearn import preprocessing
import numpy as np
import pandas as pd
import typing
from sortedcontainers import SortedKeyList


def edge_detection(df, period=3):
    print("test")
    def edge(col):
        mean = col.mean()
        if col[0] > mean and col[-1] > mean:
            return 1
        elif col[0] < mean and col[-1] < mean:
            return -1
        else:
            return 0
    return df.rolling(period, center=True).apply(edge, raw=True)

# rescale all prices, so they are between 0 and 1
def rescale_prices(ohlc_series, rescale_digits=3):
    scaled_ohlc = (ohlc_series - min(ohlc_series)) / (max(ohlc_series) - min(ohlc_series))
    rounded_ohlc = scaled_ohlc.round(rescale_digits)
    return rounded_ohlc


def ta_trend_lines(df: pd.Series,
                   edge_periods=3,
                   rescale_digits=4,
                   degrees=(-90, 90),
                   angles=30,
                   rho_digits=2,
                   edge_detect='mean',
                   **kwargs
                   ) -> typing.Tuple[pd.DataFrame, pd.DataFrame]:
    
    assert df.ndim == 1 or len(df.columns) == 1, "Trend lines can only be calculated on a series"

    # edge detection
    rescaled = rescale_prices(df, rescale_digits)
    edge_or_not = edge_detection(rescaled)

    # set up spaces
    x = np.linspace(0, 1, len(rescaled))
    y = rescaled.values.reshape(x.shape)
    edge_x_index = np.arange(0, len(rescaled))[edge_or_not != 0]
    edge_x = x[edge_or_not != 0]
    edge_y = y[edge_or_not != 0]
    thetas = np.deg2rad(np.linspace(*degrees, len(edge_x) if angles is None else angles))

    # pre compute angeles, calculate rho's
    cos_theta = np.cos(thetas)
    sin_theta = np.sin(thetas)

    if angles is None:
        # this matrix operation might be more optimized
        rhos = np.outer(cos_theta, edge_x) + np.outer(sin_theta, edge_y)
    else:
        rhos = np.vstack([edge_x[i] * cos_theta + edge_y[i] * sin_theta for i in range(len(edge_x))]).T

    # round rhos and construct a lookup table to map back from theta/rho to x/y
    rhos, time_value_lookup_table = np.around(rhos, rho_digits), {}

    for index, rho in np.ndenumerate(rhos):
        k = (thetas[index[0]], rho)
        time = df.index[edge_x_index[index[1]]]
        value = df.iloc[edge_x_index[index[1]]]

        if k in time_value_lookup_table:
            time_value_lookup_table[k].add((time, value))
        else:
            time_value_lookup_table[k] = SortedKeyList([(time, value)], key=lambda x: x[0])

    # setup the hugh space (plots nice sinusoid's
    hough_space = pd.DataFrame(rhos, index=thetas)

    # filtering
    unique_rhos = np.unique(hough_space)

    def accumulator(row):
        rhos, counts = np.unique(row, return_counts=True)
        s = pd.Series(0, index=unique_rhos)
        s[rhos] = counts
        return s

    # generate a data frame of counts with shape [angels, rhos]
    accumulated = hough_space.apply(accumulator, axis=1)

    # build lookups for filtering
    theta_indices, rho_indices = np.unravel_index(np.argsort(accumulated.values, axis=None), accumulated.shape)
    touches = []
    distances = []
    points = []

    for i in range(len(theta_indices)):
        tp = (thetas[theta_indices[i]], unique_rhos[rho_indices[i]])

        if tp in time_value_lookup_table:
            p = time_value_lookup_table[tp]
            if len(p) > 1:
                touches.append(len(p))
                distances.append(p[-1][0] - p[0][0] if len(p) > 1 else 0)
                points.append(p)

    line_lookup_table = pd.DataFrame(
        {
            "touch": touches,
            "distance": distances,
            "points": points
        },
        index=range(len(points), 0, -1)
    )

    return accumulated, line_lookup_table


# find turning points and use them as edge detection

# apply the Hough transformation

# filter the best candidates for nice trend lines

