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
from DataFlatDB import DataFlatDB
from DataDownload import DataDownload
from LinearReg_Trendline import Trendline_Drawing
from Visualize import visualize_ticker
# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import time


# 1. retrieve list of current symbols
dir_data_obj = DataFlatDB(popular_paths["current tickers"])
current_df = dir_data_obj.retrieve_data("all_current_tickers.csv")
list_curr_tickers = current_df["symbol"].tolist()

# 2. download data and add it to csv
# one caveat with the current method: there is no verfication
# that you are downloading the right thing into the right folder
dir_data_obj.change_dir(popular_paths["historical 1 week"])
downloader = DataDownload()
multiplier = 1
timespan = "week"
for ticker in list_curr_tickers:
    new_df = downloader.dwn_price_data(ticker=ticker,
                                       multiplier=multiplier,
                                       timespan=timespan)
    dir_data_obj.add_data(ticker, new_df)

    



# data_obj = DataManager() 
# start = time.time()
# params = {'multiplier' : 1, 'timeframe' : 'day'}
# data_obj.get_all_current_price_data(params)
# end = time.time()
# total = end - start
# print(f"Finished in {total} seconds")




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
