from DataExtract import retrieve_ticker_data

from LinearReg_Trendline import Trendline_Drawing

from Visualize import visualize_ticker

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd


ohlc_data = retrieve_ticker_data("roku")
trendline_obj = Trendline_Drawing(ohlc_data)

distances = [5, 10, 20, 50]

trendline_coordinates = []

# for distance in distances:
extrema_distance = 5
trendline_length = 10
precisesness = 5 # how many peaks ("touches") you want in a trendline (2 is minimumu)
trendlines_drawn = 1 # 1 provides cleaner results
trendline_obj.identify_lows_highs(ohlc_type="Low", distance=extrema_distance)
trendline_obj.identify_lows_highs(ohlc_type="High", distance=extrema_distance)

ascending_df = trendline_obj.identify_trendlines_LinReg(extreme="Low", 
                                                        min_days_out=trendline_length, 
                                                        precisesness=precisesness,
                                                        max_trendlines_drawn= trendlines_drawn)

descending_df = trendline_obj.identify_trendlines_LinReg(extreme="High", 
                                                            min_days_out=trendline_length, 
                                                            precisesness=precisesness,
                                                            max_trendlines_drawn=trendlines_drawn)
trendline_coordinates.append(ascending_df)
trendline_coordinates.append(descending_df)
both_lines_df = pd.concat(trendline_coordinates)

visualize_ticker(ohlc_data, both_lines_df)