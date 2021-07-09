from DataExtract import retrieve_ticker_data

from HoughTransform_ByHand import hough_trend_lines
from LinearReg_Trendline import identify_trendlines_LinReg

from Visualize import visualize_ticker

import datetime as dt
import matplotlib.pyplot as plt


ohlc_data = retrieve_ticker_data("TSLA")
# accumulated, ranked_lines = hough_trend_lines(ohlc_data["Low"])


ohlc_data = identify_trendlines_LinReg(ohlc_data, dt.date(2020,1,1), dt.date(2020,8, 1))
visualize_ticker(ohlc_data, ranked_lines)