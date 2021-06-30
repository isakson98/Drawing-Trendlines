from HoughTransform_Trendline import rescale_prices, ta_trend_lines

from DataExtract import retrieve_ticker_data
from LinearReg_Trendline import identify_trendlines_LinReg

from datetime import timedelta

import matplotlib.pyplot as plt


ohlc_data = retrieve_ticker_data("TSLA")
accumulated, ranked_lines = ta_trend_lines(ohlc_data["Low"])

lines = ranked_lines[ranked_lines["distance"] > timedelta(days=255)]
ohlc_data["Close"].plot(figsize=(15, 8))
for i, r in lines.iterrows():
    x = r["points"][0][0], r["points"][-1][0]
    y = r["points"][0][1], r["points"][-1][1]
    plt.plot(x, y)

plt.show()


# ohlc_data = identify_trendlines_LinReg(ohlc_data, dt.date(2020,1,1), dt.date(2020,8, 1))