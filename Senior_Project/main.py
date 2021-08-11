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
from progressbar import progressbar


#############################################################################   
# create new files with highs and lows for all tickers (current and delisted)
############################################################################# 

DISTANCE = 5

dir_list = popular_paths['historical 1 day']['dir_list']
raw_data_obj = DataFlatDB(dir_list)

dir_list = popular_paths['extrema 1 day']['dir_list']
extreme_dir_obj = DataFlatDB(dir_list)

list_raw_ticker_file_names = raw_data_obj.retrieve_all_file_names()
# TODO -> check if file exists
for index in progressbar(range(len(list_raw_ticker_file_names))):
    file_name = list_raw_ticker_file_names[index]
    # retrieve raw price data
    stock_df = raw_data_obj.retrieve_data(file_name)

    # verify processed file existence
    file_name_content = file_name.split("_")
    ticker_name = file_name_content[0]
    full_processed_file_name = ticker_name + extreme_dir_obj.suffix
    file_precense = extreme_dir_obj.verify_path_existence(full_processed_file_name)

    # if processed file exists, append to the file, only examine last portion of
    if file_precense:
        ticker_high_low_df = extreme_dir_obj.retrieve_data(full_processed_file_name)
        ticker_high_low_df_last_date = ticker_high_low_df.at("t", -1)
        # get raw data 

    else:
        # get lows and highs
        processing_obj = TickerProcessing(stock_df)
        highs_stock_df = processing_obj.identify_lows_highs(extrema_type="h", distance=DISTANCE)
        lows_stock_df = processing_obj.identify_lows_highs(extrema_type="l", distance=DISTANCE)
        if len(highs_stock_df) == 0 or len(lows_stock_df) == 0:
            continue
        # process concatanation
        both_high_low_df = pd.concat([highs_stock_df, lows_stock_df])
        both_high_low_df.fillna(False, inplace=True)
        both_high_low_df.sort_values("t", inplace=True, kind="heapsort") #heapsort cause "t" always has same num digits
        # get ticker name to save data
        extreme_dir_obj.add_data(ticker_name, both_high_low_df)












