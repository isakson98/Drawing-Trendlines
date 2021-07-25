from DataExtract import retrieve_ticker_data

from LinearReg_Trendline import Trendline_Drawing

from Visualize import visualize_ticker

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd


ohlc_data = retrieve_ticker_data("TSLA")
trendline_obj = Trendline_Drawing(ohlc_data)

touches = [2, 3, 4, 5 ]

# trendline_coordinates = []

# for distance in distances:
extrema_distance = 5
trendline_length = 10
trendlines_drawn = 1 # 1 provides cleaner results
# precisesness = 5 # how many peaks ("touches") you want in a trendline (2 is minimumu)

trendline_obj.identify_lows_highs(ohlc_type="High", distance=extrema_distance)
for precisesness in touches:
    descending_df = trendline_obj.identify_trendlines_LinReg(extreme="High", 
                                                             min_days_out=trendline_length, 
                                                             precisesness=precisesness,
                                                             max_trendlines_drawn=trendlines_drawn)
    visualize_ticker(ohlc_data, descending_df)

# trendline_coordinates.append(ascending_df)
# trendline_coordinates.append(descending_df)
# both_lines_df = pd.concat(trendline_coordinates)

