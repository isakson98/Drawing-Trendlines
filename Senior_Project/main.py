'''

if new type of data arrives -> manually create a folder or reorganize stuff
then give the location to DataReceiveExtractor class

need some kind of structure that verifies the data directories


THIS OF THIS AS A CLIENT SPACE.
This is the researcher ground.
This is where you are going to request and write stuff and ask for analysis
Do not delegate everything to library classes, as this overfits stuff (no hard coding)


'''
# database module
from DataBase.popular_paths import popular_paths
from DataBase.DataFlatDB import DataFlatDB
# from DataBase.FlatDBmodification import FlatDBmodification
# from DataBase.StockScreener import ScreenerProcessor

# price processsing module
from PriceProcessing.TickerProcessing import TickerProcessing
from PriceProcessing.LinearRegTrendline import Trendline_Drawing
from PriceProcessing.Visualize import visualize_ticker

# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import random


#############################################################################   
# create new files with highs and lows for all tickers (current and delisted)
############################################################################# 
dir_list = popular_paths['historical 1 day']['dir_list']
raw_data_obj = DataFlatDB(dir_list)

dir_list = popular_paths['extrema 1 day']['dir_list']
extreme_dir_obj = DataFlatDB(dir_list)

list_raw_ticker_file_names = raw_data_obj.retrieve_all_file_names()
for file_name in list_raw_ticker_file_names:
    # retrieve raw price data
    stock_df = raw_data_obj.retrieve_data(file_name)
    # get lows and highs
    processing_obj = TickerProcessing(stock_df)
    highs_stock_df = processing_obj.identify_lows_highs(extrema_type="h", distance = 5)
    lows_stock_df = processing_obj.identify_lows_highs(extrema_type="l", distance = 5)
    if len(highs_stock_df) == 0 or len(lows_stock_df) == 0:
        continue
    # process concatanation
    both_high_low_df = pd.concat([highs_stock_df, lows_stock_df])
    both_high_low_df.fillna(False, inplace=True)
    both_high_low_df.sort_values("t", inplace=True, kind="heapsort") #heapsort cause "t" always has same num digits
    # get ticker name to save data
    file_name_content = file_name.split("_")
    ticker_name = file_name_content[0]
    extreme_dir_obj.add_data(ticker_name, both_high_low_df)












