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
from PriceProcessing.RawPriceProcessing import RawPriceProcessing
from PriceProcessing.TrendlineDrawing import TrendlineDrawing
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

    '''
    params:
        include_delisted -> true or false whether you want to include delisted as well
    This is a frequently used feature. Retriving available ticker names.

    This function returns list of file names, not merely ticker names

    returns:
        daily_raw_file_names -> list of daily file names (with extensions) but not paths (not needed)
    '''
    def retrieve_daily_list_file_names(self, include_delisted:bool()):
        daily_raw_file_names = []
        if include_delisted:
            data_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
            daily_raw_file_names = data_obj.retrieve_all_file_names()

        else:
            # retrieve list of current tickers
            dir_list = popular_paths['current tickers']["dir_list"]
            db_obj =  DataFlatDB(dir_list)
            current_df = db_obj.retrieve_data("all_current_tickers.csv")
            list_cur_tickers = current_df["symbol"].tolist()

            # retrieve suffix of the directory
            dir_list = popular_paths['historical 1 day']["dir_list"]
            db_obj.change_dir(dir_list)
            needed_suf = db_obj.suffix

            # create a list of files names 
            daily_raw_file_names = [ticker + needed_suf for ticker in list_cur_tickers]

        return daily_raw_file_names

    #############################################################################
    # RETRIEVING RAW PRICE AND EXTREMA AND PLOTTING THEM 
    #############################################################################
    def retrieve_RawPrice_and_Extrema_and_plot_them(self, STOCK_TO_VISUALIZE):
        raw_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
        raw_df = raw_obj.retrieve_data(STOCK_TO_VISUALIZE+raw_obj.suffix)
        
        trendline_obj = TrendlineDrawing(raw_df, starting_extrema_df=raw_df["h_extremes_5"])
        trendline_df = trendline_obj.identify_trendlines_LinReg(distance=5, extrema_type="h", precisesness=2, max_trendlines_drawn=1)

        visualize_ticker(raw_df, trendline_df)

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

    def retrieve_all_current_ticker_names(self):
        # retrieve list of current tickers
        dir_list = popular_paths['current tickers']["dir_list"]
        db_obj =  DataFlatDB(dir_list)
        current_df = db_obj.retrieve_data("all_current_tickers.csv")
        list_cur_tickers = current_df["symbol"].tolist()
        return list_cur_tickers

    #############################################################################   
    # update daily candles for all current tickers
    ############################################################################# 

    def get_higher_highs_one_stock_daily(self, STOCK_TO_VISUALIZE):

        data_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
        ohlc_df = data_obj.retrieve_data(STOCK_TO_VISUALIZE+data_obj.suffix)

        tick_obj = RawPriceProcessing()
        # get higher highs
        higher_highs = tick_obj.get_higher_extrema(ohlc_df, extrema="h", distance=5, above_last_num_highs=2)
        # get highs that are higher than previous higher highs
        higher_highs = tick_obj.get_higher_extrema(higher_highs, extrema="h", distance=5, above_last_num_highs=1)

        return higher_highs

    #############################################################################   
    # update daily candles raw volume
    ############################################################################# 
    def draw_descending_trendline_on_bullish_stock(self, STOCK_TO_VISUALIZE, precision=[3, 4, 5, 6]):
        
        raw_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
        raw_df = raw_obj.retrieve_data(STOCK_TO_VISUALIZE+raw_obj.suffix)

        def_higher_highs = self.get_higher_highs_one_stock_daily(STOCK_TO_VISUALIZE)

        for prec in precision:    
            trendline_obj = TrendlineDrawing(raw_df, starting_extrema_df=def_higher_highs, breakout_based_on="strong close")
            trendline_df = trendline_obj.identify_trendlines_LinReg(distance=5, 
                                                                    extrema_type="h", 
                                                                    precisesness=prec, 
                                                                    max_trendlines_drawn=1)  

            desc_trendlines = trendline_obj.remove_ascending_trendlines(trendline_df)  

            visualize_ticker(all_ohlc_data=raw_df, 
                                peaks_df=def_higher_highs,
                                distance=5,
                                trendlines=desc_trendlines)

    #############################################################################   
    # update daily candles raw volume
    ############################################################################# 
    def add_latest_avg_vol_to_raw_daily(self, include_delisted):

        # create a list of files names 
        daily_raw_file_names = self.retrieve_daily_list_file_names(include_delisted=include_delisted)

        partial_fun_params = {'multiple' : 1, 'timespan' : 'day', 'candle_window' : 20,}
        flat_db_manip_obj = FlatDBRawMod()
        flat_db_manip_obj.parallel_ticker_workload(proc_function = flat_db_manip_obj.add_freshest_average_volume, 
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_raw_file_names,
                                                n_core=7)

    #############################################################################   
    # update daily candles raw volume (on recent )
    ############################################################################# 
    def add_latest_highs_lows_to_raw_daily(self, include_delisted):
        # create a list of files names 
        daily_raw_file_names = self.retrieve_daily_list_file_names(include_delisted=include_delisted)

        db_changes_obj = FlatDBRawMod()
        partial_fun_params = {"multiple" : 1, "timespan" : "day", "distance" : 5}
        db_changes_obj.parallel_ticker_workload(db_changes_obj.add_freshest_extrema_on_tickers,
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_raw_file_names)

    #############################################################################   
    # filter through higher highs 
    ############################################################################# 
    '''
    params:
        include_delisted -> do you want to include delisted or nah
        avg_v_min -> minimum average volume to qualify higher high as acceptable
        avg_v_distance -> parameter of the average volume (20 is the usual one)

    This function is used to detemine useful entry points 
    
    '''
    def get_high_quality_higher_highs(self, include_delisted, avg_v_min, avg_v_distance=20):

        # TODO: make sure you determine whether you accept full file names or just tickers
        #       as arguments, not both, especially in the same class!

        # get all tickers 
        daily_raw_file_names = self.retrieve_daily_list_file_names(include_delisted=include_delisted)

        # get all higher highs from all tickers

        # filter by average volume

        # save results?



