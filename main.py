from DataExtract import retrieve_ticker_data

from HoughTransform_ByHand import hough_trend_lines
from LinearReg_Trendline import (identify_trendlines_LinReg, 
                                 identify_lows_highs)

from Visualize import visualize_ticker

import datetime as dt
import matplotlib.pyplot as plt


ohlc_data = retrieve_ticker_data("NIO")
# accumulated, technicals_df = hough_trend_lines(ohlc_data["Low"])
# visualize_ticker(ohlc_data, technicals_df)

identify_lows_highs(ohlc_data, "Low", 5, False)
ohlc_data, technicals_df = identify_trendlines_LinReg(ohlc_data, dt.date(2020,9,30), dt.date(2020,12, 30))
visualize_ticker(ohlc_data, technicals_df)