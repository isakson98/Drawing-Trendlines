'''

if new type of data arrives -> manually create a folder or reorganize stuff
then give the location to DataReceiveExtractor class

need some kind of structure that verifies the data directories


THIS OF THIS AS A CLIENT SPACE.
This is the researcher ground.
This is where you are going to request and write stuff and ask for analysis
Do not delegate everything to library classes, as this overfits stuff (no hard coding)


'''
# man made, database module
from DataBase.popular_paths import popular_paths
from DataBase.FlatDBmodification import FlatDBmodification
from DataBase.StockScreener import ScreenerProcessor
from DataBase.DataFlatDB import DataFlatDB

# 
from PriceProcessing.LinearRegTrendline import Trendline_Drawing
from PriceProcessing.Visualize import visualize_ticker

# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import random

if __name__ == '__main__':

    #############################################################################
    # DOWNLOADING DATA FOR DELISTED TICKERS
    #############################################################################

    # retrieve delisted tickers
    flat_ob = DataFlatDB(popular_paths["delisted tickers"]["dir_list"])
    delisted_df = flat_ob.retrieve_data("all_delisted_tickers.csv")
    delisted_list = delisted_df["symbol"].tolist()

    # list in ascending order time wise, so first thread will get most available tickers
    random.shuffle(delisted_list)

    # download data for delisted tickers
    dir_list = popular_paths["historical 1 day"]["dir_list"]
    params = popular_paths["historical 1 day"]["params"]
    flat_mod = FlatDBmodification()
    flat_mod.threaded_add_new_price_data(dir_list=dir_list, 
                                        params=params, 
                                        update=False, 
                                        tickers_to_update=delisted_list)

    #############################################################################   
    # update current ticker csv and delisted csv
    #############################################################################
    refresh_obj = FlatDBmodification()
    refresh_obj.update_current_ticker_list()

    #############################################################################   
    # retrieve daily candles for all current tickers
    ############################################################################# 
    refresh_obj = FlatDBmodification()
    params = popular_paths['historical 1 day']["params"]
    dir_list = popular_paths['historical 1 day']["dir_list"]
    refresh_obj.threaded_add_new_price_data(dir_list, params, update=False)

    #############################################################################   
    # update daily candles for all current tickers
    ############################################################################# 
    refresh_obj = FlatDBmodification()
    params = popular_paths['historical 1 day']["params"]
    dir_list = popular_paths['historical 1 day']["dir_list"]
    refresh_obj.threaded_add_new_price_data(dir_list, params, update=True)

    #############################################################################   
    # update daily candles for all current tickers
    ############################################################################# 
    
    # ---------------------------- TRENDLINE MATERIAL --------------------------------- # 
    flat_ob = DataFlatDB()
    file_name = "AMC" + flat_ob.suffix
    amc_df = flat_ob.retrieve_data(file_name)

    trendline_obj = Trendline_Drawing(amc_df)
    touches = [2, 3, 4, 5 ]  # how many peaks ("touches") you want in a trendline (2 is minimumu)
    extrema_distance = 5
    trendline_length = 10
    trendlines_drawn = 1 # 1 provides cleaner results
    trendline_obj.identify_lows_highs(extrema_type="High", distance=extrema_distance)
    for precisesness in touches:
        descending_df = trendline_obj.identify_trendlines_LinReg(extreme="High", 
                                                                min_days_out=trendline_length, 
                                                                precisesness=precisesness,
                                                                max_trendlines_drawn=trendlines_drawn)
        visualize_ticker(amc_df, descending_df)

