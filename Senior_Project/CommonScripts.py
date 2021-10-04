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
from pandas.core.frame import DataFrame
from DataBase.popular_paths import popular_paths
from DataBase.FlatDBRawMod import FlatDBRawMod
from DataBase.FlatDBProssesedMod import FlatDBProssesedMod
from DataBase.StockScreener import ScreenerProcessor
from DataBase.DataFlatDB import DataFlatDB
from DataBase.FileConcat import FileConcat

# PriceProcessing module files
from PriceProcessing.RawPriceProcessing import RawPriceProcessing
from PriceProcessing.TrendlineDrawing import TrendlineDrawing
from PriceProcessing.TrendlineProcessing import TrendlineProcessing
from PriceProcessing.Visualize import visualize_ticker
from PriceProcessing.TrendlineFeatureDesign import TrendlineFeatureDesign

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
    # RETRIEVING DIRECTORY FILE NAMES OR TICKER SYMBOLS
    #############################################################################
    '''
    params:
        include_delisted -> true or false whether you want to include delisted as well
    This is a frequently used feature. Retriving available ticker names.

    This function returns list of file names, not merely ticker names

    returns:
        daily_raw_file_names -> list of daily file names (with extensions) but not paths (not needed)
    '''
    def retrieve_ticker_list(self, include_delisted:bool()):
        ticker_names = []
        if include_delisted:
            data_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
            ticker_names = data_obj.retrieve_all_ticker_names()
        else:
            # retrieve list of current tickers
            ticker_names = self.retrieve_all_current_ticker_names()

        return ticker_names

    def retrieve_all_raw_dir_daily_file_names(self):
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
    # PLOTTING STOCK ONLY
    #############################################################################
    def visualize_stock(self, STOCK_TO_VISUALIZE, multiple = 1, timespan = "day"):
        timeframe = str(multiple) + " " + timespan
        raw_obj = DataFlatDB(popular_paths[f"historical {timeframe}"]["dir_list"])
        raw_df = raw_obj.retrieve_data(STOCK_TO_VISUALIZE+raw_obj.suffix)

        visualize_ticker(all_ohlc_data=raw_df)

    #############################################################################   
    # update daily candles raw volume
    ############################################################################# 
    def draw_descending_trendline_on_bullish_stock(self, STOCK_TO_VISUALIZE, precision=[3, 4, 5, 6]):
        
        raw_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
        raw_df = raw_obj.retrieve_data(STOCK_TO_VISUALIZE+raw_obj.suffix)

        trendline_obj = DataFlatDB(popular_paths["bull triangles 1 day"]["dir_list"])
        trendline_df = trendline_obj.retrieve_data(STOCK_TO_VISUALIZE+trendline_obj.suffix)

        if len(trendline_df) == 0 :

            def_higher_highs = self.get_higher_highs_one_stock_daily(STOCK_TO_VISUALIZE)
            start_points_list = def_higher_highs["h_extremes_5"].index.tolist()
            trendline_obj = TrendlineDrawing(raw_df, start_points_list=start_points_list, breakout_based_on="strong close")
            trendline_pros_obj = TrendlineProcessing()
            for prec in precision:    
                trendline_df = trendline_obj.identify_trendlines_LinReg(line_unit_col="h", 
                                                                        preciseness=prec, 
                                                                        max_trendlines_drawn=2)  

                desc_trendlines = trendline_pros_obj.remove_ascending_trendlines(trendline_df)  

                visualize_ticker(all_ohlc_data=raw_df, 
                                    peaks_df=def_higher_highs,
                                    distance=5,
                                    trendlines=desc_trendlines)
        
        else:
            split_by_precision_df = trendline_df.groupby("preciseness")

            for preciseness in split_by_precision_df.groups:
                preciseness_df = split_by_precision_df.get_group(preciseness)
                visualize_ticker(all_ohlc_data=raw_df,
                                 trendlines=preciseness_df)


        

    #############################################################################   
    # update daily candles raw volume
    ############################################################################# 
    def add_latest_avg_vol_to_raw_daily(self, include_delisted):

        # create a list of files names 
        daily_available_tickers = self.retrieve_ticker_list(include_delisted=include_delisted)

        partial_fun_params = {'multiple' : 1, 'timespan' : 'day', 'candle_window' : 20}
        flat_db_manip_obj = FlatDBRawMod()
        flat_db_manip_obj.parallel_ticker_workload(proc_function = flat_db_manip_obj.add_freshest_average_volume, 
                                                   partial_fun_params=partial_fun_params,
                                                   list_ticker_names=daily_available_tickers)

    #############################################################################   
    # update daily candles raw volume (on recent )
    ############################################################################# 
    def add_latest_highs_lows_to_raw_daily(self, include_delisted):
        # create a list of files names 
        daily_available_tickers = self.retrieve_ticker_list(include_delisted=include_delisted)

        partial_fun_params = {"multiple" : 1, "timespan" : "day", "distance" : 5}
        db_changes_obj = FlatDBRawMod()
        db_changes_obj.parallel_ticker_workload(db_changes_obj.add_freshest_extrema_on_tickers,
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_available_tickers)

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
    def add_high_quality_higher_highs_daily(self, include_delisted, extrema_distance=5, avg_v_min=50000, avg_v_distance=20):

        # get all tickers 
        daily_raw_ticker = self.retrieve_ticker_list(include_delisted=include_delisted)

        # default values are the ones that have been computed, and I know exist
        partial_fun_params = {"multiple" : 1,
                              "timespan" : "day",
                              "extrema_distance":extrema_distance, 
                              "avg_v_distance" : avg_v_distance,
                              "avg_v_min":avg_v_min}

        db_changes_obj = FlatDBRawMod()
        db_changes_obj.parallel_ticker_workload(db_changes_obj.add_high_qual_higher_highs,
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_raw_ticker)


    #############################################################################   
    # update daily candles latest trendlines
    ############################################################################# 
    def add_latest_daily_bullish_triangles(self, include_delisted):

        # get all tickers 
        daily_raw_ticker = self.retrieve_ticker_list(include_delisted=include_delisted)

        # default values are the ones that have been computed, and I know exist
        partial_fun_params = {"multiple" : 1,
                              "timespan" : "day"}

        db_changes_obj = FlatDBProssesedMod()
        db_changes_obj.parallel_ticker_workload(db_changes_obj.add_bullish_desc_trendlines,
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_raw_ticker)

    '''
    
    FEATURE ENGINEERING
    
    '''
    #############################################################################   
    # update daily candles latest pole length
    ############################################################################# 
    def add_latest_pole_length(self, include_delisted):
        # get all tickers 
        daily_raw_ticker = self.retrieve_ticker_list(include_delisted=include_delisted)

        # default values are the ones that have been computed, and I know exist
        partial_fun_params = {"multiple" : 1,
                              "timespan" : "day",
                              "n_prev" : 1}

        db_changes_obj = FlatDBProssesedMod()
        db_changes_obj.parallel_ticker_workload(db_changes_obj.add_pole_length,
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_raw_ticker)  

    #############################################################################   
    # update daily candles latest pole length to flag length ratio
    ############################################################################# 
    def add_latest_pole_flag_length_ratio(self, include_delisted):
        # get all tickers 
        daily_raw_ticker = self.retrieve_ticker_list(include_delisted=include_delisted)

        # default values are the ones that have been computed, and I know exist
        partial_fun_params = {"multiple" : 1,
                              "timespan" : "day",
                              "n_prev" : 1}

        db_changes_obj = FlatDBProssesedMod()
        db_changes_obj.parallel_ticker_workload(db_changes_obj.add_pole_flag_length_ratio,
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_raw_ticker) 

    '''
    params:
        info_col -> new column that you want to be created. Also corresponds to a special dictionary
    
    '''
    #############################################################################   
    # update daily trendlines latest low of flag
    ############################################################################# 
    def add_latest_flag_low_info(self, low_info, include_delisted):
        # get all tickers 
        daily_raw_ticker = self.retrieve_ticker_list(include_delisted=include_delisted)

        # default values are the ones that have been computed, and I know exist
        partial_fun_params = {"multiple" : 1,
                              "timespan" : "day",
                              "low_info" : low_info}
                              
        db_changes_obj = FlatDBProssesedMod()
        db_changes_obj.parallel_ticker_workload(db_changes_obj.add_flag_low_info,
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_raw_ticker)  


    #############################################################################   
    # update daily candles latest pole length to flag length ratio
    ############################################################################# 
    def add_latest_pivot_flag_height_ratio(self, include_delisted):
        # get all tickers 
        daily_raw_ticker = self.retrieve_ticker_list(include_delisted=include_delisted)

        # default values are the ones that have been computed, and I know exist
        partial_fun_params = {"multiple" : 1,
                              "timespan" : "day",
                              "n_prev" : 1}

        db_changes_obj = FlatDBProssesedMod()
        db_changes_obj.parallel_ticker_workload(db_changes_obj.add_pivot_flag_height_ratio,
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_raw_ticker) 


    #############################################################################   
    # update daily candles latest pole features -> 
    ############################################################################# 
    '''
    params:
        pole_info -> pole info that you want computed
        include_delisted -> do you want to include delisted or nah

    This function updates newest pole features
    
    '''
    def add_latest_pole_features(self, pole_info, include_delisted):

        db_changes_obj = FlatDBProssesedMod()
        if pole_info not in list(db_changes_obj.pole_low_info_functions.keys()):
            raise ValueError("Invalid value for pole_info parameter")
        # get all tickers 
        daily_raw_ticker = self.retrieve_ticker_list(include_delisted=include_delisted)

        # default values are the ones that have been computed, and I know exist
        partial_fun_params = {"multiple" : 1,
                              "timespan" : "day",
                              "n_prev" : 1,
                              "pole_info" : pole_info}
                              
        db_changes_obj.parallel_ticker_workload(db_changes_obj.add_pole_info,
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_raw_ticker) 

    #############################################################################   
    # update daily candles latest pole to flag height ratio-> 
    ############################################################################# 
    '''
    params:
        include_delisted -> do you want to include delisted or nah

    This function is used to detemine the latest pole dollar range to flag dollar range
    
    '''
    def add_latest_pole_flag_height_ratio(self, include_delisted):
        # get all tickers 
        daily_raw_ticker = self.retrieve_ticker_list(include_delisted=include_delisted)

        # default values are the ones that have been computed, and I know exist
        partial_fun_params = {"multiple" : 1,
                              "timespan" : "day"}
                              
        db_changes_obj = FlatDBProssesedMod()
        db_changes_obj.parallel_ticker_workload(db_changes_obj.add_pole_flag_height_ratio,
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_raw_ticker) 

    #############################################################################   
    # update daily trendlines' labels
    ############################################################################# 
    '''
    params:
        include_delisted -> do you want to include delisted or nah

    This function is used to detemine the latest pole dollar range to flag dollar range
    
    '''
    def add_latest_labels_to_triangles(self, include_delisted):
        # get all tickers 
        daily_raw_ticker = self.retrieve_ticker_list(include_delisted=include_delisted)

        # default values are the ones that have been computed, and I know exist
        partial_fun_params = {"multiple" : 1,
                              "timespan" : "day",
                              "num_of_lows" : 2,
                              "profitable_r" : 2}
                              
        db_changes_obj = FlatDBProssesedMod()
        db_changes_obj.parallel_ticker_workload(db_changes_obj.add_labels_triangles,
                                                partial_fun_params=partial_fun_params,
                                                list_ticker_names=daily_raw_ticker)


    #############################################################################   
    # Concatanates all the files in a directory into a single csv
    ############################################################################# 
    '''
    params:
        path -> path of the directory whose files you want all into one
        path_to_save_in -> path to the end destination
        file_name -> name of file

    One of the final steps of this whole project.
    After separately adding features to trendlines, you merge the content of
    one directory into a single big csv for data cleaning/prep and training
    
    '''
    def concat_all_directory_files(self, path_to_concat, path_to_save_in, file_name):
        
        
        file_concat_obj = FileConcat(path_to_concat)
        file_concat_obj.concat_files(path_to_save_in, file_name)

