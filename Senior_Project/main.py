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
from DataBase.FlatDBProssesedMod import FlatDBProssesedMod

# price processsing module
from PriceProcessing.TickerProcessing import TickerProcessing
from PriceProcessing.LinearRegTrendline import Trendline_Drawing
from PriceProcessing.Visualize import visualize_ticker

# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

#############################################################################   
# create new files with highs and lows for all tickers (current and delisted)
############################################################################# 

if __name__ == '__main__':

    # # 
    # STOCK_TO_VISUALIZE = "TREX"
    # raw_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
    # raw_df = raw_obj.retrieve_data(STOCK_TO_VISUALIZE+raw_obj.suffix)

    # extrema_obj = DataFlatDB(popular_paths["extrema 1 day"]["dir_list"])
    # extrema_df = extrema_obj.retrieve_data(STOCK_TO_VISUALIZE+extrema_obj.suffix)

    # visualize_ticker(raw_df, extrema_df)


    raw_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
    raw_file_names = raw_obj.retrieve_all_file_names()

    partial_params = {'multiple':1, 'timespan':"day", 'distance':5}
    pross_mod_obj = FlatDBProssesedMod()
    pross_mod_obj.parallel_save_extrema(partial_params, raw_file_names, 1)
