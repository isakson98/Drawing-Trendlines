from DataExtract import retrieve_ticker_data

from HoughTransform_ByHand import hough_trend_lines
from LinearReg_Trendline import (identify_decending_trendlines_LinReg, 
                                 identify_lows_highs)

from Visualize import visualize_ticker

import datetime as dt
import matplotlib.pyplot as plt


ohlc_data = retrieve_ticker_data("NET")
ohlc_data = identify_lows_highs(ohlc_data, "High", 10)
ohlc_data, technicals_df = identify_decending_trendlines_LinReg(ohlc_data, min_days_out=10, precisesness=2)
visualize_ticker(ohlc_data, technicals_df)