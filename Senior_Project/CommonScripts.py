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
from DataBase.FlatDBRawMod import FlatDBRawMod
from DataBase.StockScreener import ScreenerProcessor
from DataBase.DataFlatDB import DataFlatDB

# PriceProcessing module files
from PriceProcessing.TickerProcessing import TickerProcessing
from PriceProcessing.LinearRegTrendline import Trendline_Drawing
from PriceProcessing.Visualize import visualize_ticker

# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import random

##################################################################################################
                                #   COMMON SCRIPTS, USING DIFFERENT LIBRARIES  #
##################################################################################################
class CommonScripts:

    #############################################################################
    # RETRIEVING RAW PRICE AND EXTREMA AND PLOTTING THEM 
    #############################################################################
    def retrieve_RawPrice_and_Extrema_and_plot_them(self, STOCK_TO_VISUALIZE):
        raw_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
        raw_df = raw_obj.retrieve_data(STOCK_TO_VISUALIZE+raw_obj.suffix)

        extrema_obj = DataFlatDB(popular_paths["extrema 1 day"]["dir_list"])
        extrema_df = extrema_obj.retrieve_data(STOCK_TO_VISUALIZE+extrema_obj.suffix)
        
        trendline_obj = Trendline_Drawing(raw_df, extrema_df)
        trendline_df = trendline_obj.identify_trendlines_LinReg(distance=5, extrema_type="h", precisesness=2, max_trendlines_drawn=1)

        visualize_ticker(raw_df, extrema_df, trendline_df)

    #############################################################################
    # DOWNLOADING DATA FOR DELISTED TICKERS
    #############################################################################
    def download_delisted_raw_tickers(self):
        # retrieve delisted tickers
        flat_ob = DataFlatDB(popular_paths["delisted tickers"]["dir_list"])
        delisted_df = flat_ob.retrieve_data("all_delisted_tickers.csv")
        delisted_list = delisted_df["symbol"].tolist()

        # list in ascending order time wise, so first thread will get most available tickers
        random.shuffle(delisted_list)

        # download data for delisted tickers
        dir_list = popular_paths["historical 1 day"]["dir_list"]
        params = popular_paths["historical 1 day"]["params"]
        flat_mod = FlatDBRawMod()
        flat_mod.threaded_add_new_price_data(dir_list=dir_list, 
                                            params=params, 
                                            update=False, 
                                            tickers_to_update=delisted_list)

    #############################################################################   
    # update current ticker csv and delisted csv
    #############################################################################
    def update_file_current_stocks(self):
        refresh_obj = FlatDBRawMod()
        refresh_obj.update_current_ticker_list()

    #############################################################################   
    # update daily candles for all current tickers
    ############################################################################# 
    def update_last_daily_prices_current_tickers(self):
        refresh_obj = FlatDBRawMod()
        params = popular_paths['historical 1 day']["params"]
        dir_list = popular_paths['historical 1 day']["dir_list"]
        refresh_obj.threaded_add_new_price_data(dir_list, params, update=True)

    #############################################################################   
    # update daily candles for all current tickers
    ############################################################################# 
    def retrieve_all_raw_dir_data(self):
        dir_list = popular_paths['historical 1 day']["dir_list"]
        refresh_obj = DataFlatDB(dir_list)
        raw_file_names = refresh_obj.retrieve_all_file_names()
        return raw_file_names

    #############################################################################   
    # update daily candles for all current tickers
    ############################################################################# 

    def get_higher_highs_one_stock(self, STOCK_TO_VISUALIZE):
        raw_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
        raw_df = raw_obj.retrieve_data(STOCK_TO_VISUALIZE+raw_obj.suffix)

        extrema_obj = DataFlatDB(popular_paths["extrema 1 day"]["dir_list"])
        extrema_df = extrema_obj.retrieve_data(STOCK_TO_VISUALIZE+extrema_obj.suffix)

        tick_obj = TickerProcessing()
        # get higher highs
        higher_highs = tick_obj.get_higher_extrema(extrema_df, extrema="h", distance=5, above_last_num_highs=2)
        # get highs that are higher than previous higher highs
        higher_highs = tick_obj.get_higher_extrema(higher_highs, extrema="h", distance=5, above_last_num_highs=1)

        return higher_highs

    def draw_descending_trendline_on_bullish_stock(self, STOCK_TO_VISUALIZE, precision=[3, 4, 5, 6]):
        
        raw_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
        raw_df = raw_obj.retrieve_data(STOCK_TO_VISUALIZE+raw_obj.suffix)

        def_higher_highs = self.get_higher_highs_one_stock(STOCK_TO_VISUALIZE)

        for prec in precision:
            trendline_obj = Trendline_Drawing(raw_df, def_higher_highs, breakout_based_on="strong close")
            trendline_df = trendline_obj.identify_trendlines_LinReg(distance=5, 
                                                                    extrema_type="h", 
                                                                    precisesness=prec, 
                                                                    max_trendlines_drawn=2)  

            desc_trendlines = trendline_obj.remove_ascending_trendlines(trendline_df)  
            visualize_ticker(raw_df, def_higher_highs, desc_trendlines)

    #############################################################################   
    # update daily candles raw volume
    ############################################################################# 
    def add_latest_avg_vol_to_raw_daily(self):
        data_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
        daily_raw_file_names = data_obj.retrieve_all_file_names()

        partial_fun_params = {'multiple' : 1, 'timespan' : 'day', 'candle_window' : 20,}
        flat_db_manip_obj = FlatDBRawMod()
        flat_db_manip_obj.parallel_ticker_workload(proc_function = flat_db_manip_obj.add_freshest_average_volume, 
                                                partial_fun_params=partial_fun_params,
                                                list_raw_ticker_file_names=daily_raw_file_names,
                                                n_core=7)

