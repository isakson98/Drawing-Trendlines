from DataExtract import retrieve_ticker_data

from LinearReg_Trendline import (identify_trendlines_LinReg, 
                                 identify_lows_highs)

from Visualize import visualize_ticker

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd


ohlc_data = retrieve_ticker_data("mrna")
ohlc_data = identify_lows_highs(ohlc_data, 
                                ohlc_type="Low",
                                distance=10)

ohlc_data, ascending_df = identify_trendlines_LinReg(ohlc_data, 
                                                      extreme="Low", 
                                                      min_days_out=10, 
                                                      precisesness=3)

ohlc_data = identify_lows_highs(ohlc_data, 
                                ohlc_type="High",
                                distance=10)

ohlc_data, descending_df = identify_trendlines_LinReg(ohlc_data, 
                                                      extreme="High", 
                                                      min_days_out=10, 
                                                      precisesness=3)

both_lines_df = pd.concat([ascending_df, descending_df])

visualize_ticker(ohlc_data, both_lines_df)