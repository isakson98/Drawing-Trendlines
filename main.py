from DataExtract import retrieve_ticker_data

from HoughTransform_ByHand import hough_trend_lines
from LinearReg_Trendline import (identify_decending_trendlines_LinReg, 
                                 identify_lows_highs)

from Visualize import visualize_ticker

import datetime as dt
import matplotlib.pyplot as plt


ohlc_data = retrieve_ticker_data("NIO")
# accumulated, technicals_df = hough_trend_lines(ohlc_data["Low"])
# visualize_ticker(ohlc_data, technicals_df)

ohlc_data = identify_lows_highs(ohlc_data, "High", 5)
ohlc_data, technicals_df = identify_decending_trendlines_LinReg(ohlc_data)
visualize_ticker(ohlc_data, technicals_df)