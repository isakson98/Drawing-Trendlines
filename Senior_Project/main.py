'''

if new type of data arrives -> manually create a folder or reorganize stuff
then give the location to DataReceiveExtractor class

need some kind of structure that verifies the data directories


THIS OF THIS AS A CLIENT SPACE.
This is the researcher ground.
This is where you are going to request and write stuff and ask for analysis
Do not delegate everything to library classes, as this overfits stuff (no hard coding)


'''
# man made
from popular_paths import popular_paths
from FlatDBmodification import FlatDBmodification

# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

refresh_obj = FlatDBmodification()
# refresh_obj.update_current_ticker_list()


params = popular_paths['historical 1 day']["params"]
dir_list = popular_paths['historical 1 day']["dir_list"]
refresh_obj.threaded_add_new_price_data(dir_list, params, update=True)


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
