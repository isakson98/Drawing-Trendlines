from DataReceiveExtractor import DataManager

from LinearReg_Trendline import Trendline_Drawing

from Visualize import visualize_ticker

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

import time

data_obj = DataManager() 

start = time.time()
params = {'multiplier' : 1, 'timeframe' : 'day'}
data_obj.get_all_current_price_data(params)
end = time.time()

total = end - start
print(f"Finished in {total} seconds")

# params["name"] = "tsla"
# data_obj.get_price_data(params)








# ---------------------------- TRENDLINE MATERIAL --------------------------------- #
# trendline_obj = Trendline_Drawing(ohlc_data)
# touches = [2, 3, 4, 5 ]  # how many peaks ("touches") you want in a trendline (2 is minimumu)
# extrema_distance = 5
# trendline_length = 10
# trendlines_drawn = 1 # 1 provides cleaner results
# trendline_obj.identify_lows_highs(ohlc_type="High", distance=extrema_distance)
# for precisesness in touches:
#     descending_df = trendline_obj.identify_trendlines_LinReg(extreme="High", 
#                                                              min_days_out=trendline_length, 
#                                                              precisesness=precisesness,
#                                                              max_trendlines_drawn=trendlines_drawn)
#     visualize_ticker(ohlc_data, descending_df)
