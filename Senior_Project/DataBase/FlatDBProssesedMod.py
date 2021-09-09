from random import shuffle
import numpy as np
import multiprocessing as mp
import pandas as pd

from PriceProcessing.TrendlineDrawing import TrendlineDrawing
from PriceProcessing.TrendlineProcessing import TrendlineProcessing
from PriceProcessing.TrendlineFeatureDesign import TrendlineFeatureDesign

from DataBase.DataFlatDB import DataFlatDB
from DataBase.popular_paths import popular_paths


TOTAL_PROCESSES = mp.cpu_count() - 1
# TEMP
TOTAL_PROCESSES = 1

'''

This class allows to perform modifications of data in the processed
section of the database.

Since it deals with processing files, a cpu-intensive task, instead of
utilizing threads like FlatDBRawMod class did, this class is going to use
processes instead.

'''
class FlatDBProssesedMod:

    process_lock = mp.Lock()
    list_incrementer = 0


    ################################################################################
                        # PROCESSED PRICE MANIPULATION # (MULTI - PROCESSED)
    ################################################################################

    '''
    params:
        list_ticker_names -> list of tickers that need to be processed (TICKERS NOT FILE NAMES!)
        kwargs -> multiple -> pt.1 of key composition for needed dir
                  timespan -> pt.2 of key composition for needed dir
    '''
    def add_bullish_desc_trendlines(self, list_ticker_names, list_increment : mp.Value, **kwargs):

        multiple, timespan = kwargs['multiple'], kwargs['timespan']
        # init db objects and verify that the directories exist 
        try:
            dir_params = str(multiple) + " " + timespan
            dir_list = popular_paths[f'historical {dir_params}']['dir_list']
            raw_data_obj = DataFlatDB(dir_list)
            needed_suf = raw_data_obj.suffix

            dir_list = popular_paths[f'bull triangles {dir_params}']['dir_list']
            trend_db_obj = DataFlatDB(dir_list)
        except:
            error_statement = f"Wrong directory parameters {dir_params}" 
            raise ValueError(error_statement)

        # create a list of files names 
        list_raw_ticker_file_names = [ticker + needed_suf for ticker in list_ticker_names]
        # exit when the shared memory variable reaches the end
        while list_increment.value != len(list_raw_ticker_file_names) - 1:
            with list_increment.get_lock():
                list_increment.value += 1
            index = list_increment.value
            file_name = list_raw_ticker_file_names[index]
            if index % 100 == 0 and index != 0:
                self.process_lock.acquire()
                print(f"Process identified extrema on {index} tickers")
                self.process_lock.release()
            # retrieve raw price data
            stock_df = raw_data_obj.retrieve_data(file_name)
            if len(stock_df) == 0: continue
            
            # determine the starting index
            trend_file_name = list_ticker_names[index] + trend_db_obj.suffix
            trend_existing_df = pd.DataFrame()
            trend_df_exists = trend_db_obj.verify_path_existence(trend_file_name)
            if trend_df_exists: 
                trend_existing_df = trend_db_obj.retrieve_data(trend_file_name)
                last_timestamp_performed_on = trend_existing_df["t_start"].iloc[-1]
                stock_df = stock_df[stock_df["t"] >= last_timestamp_performed_on]

            # get list of indices that match high quality higher highs
            hh_hq_t = stock_df["t"].loc[stock_df["hq_hh"]==True]
            hh_hq_index_list = hh_hq_t.index.tolist()
                
            # if there are no high quality higher highs, there are no starting points for the algo
            if len(hh_hq_index_list) == 0: continue

            trendline_obj = TrendlineDrawing(ohlc_raw=stock_df, 
                                             start_points_list=hh_hq_index_list, 
                                             breakout_based_on="strong close")
            trendline_pros_obj = TrendlineProcessing()
            preciseness = [2, 3, 4, 5, 6, 8]
            # collecting groups of different types of descending trendlines
            existing_df_len = len(trend_existing_df)
            new_trendline_df = pd.DataFrame()
            for one_prec in preciseness:
                one_prec_df = trendline_obj.identify_trendlines_LinReg(line_unit_col="h", preciseness=one_prec)
                new_trendline_df = new_trendline_df.append(one_prec_df)
            trendline_obj.clear_cache()

            new_trendline_df = trendline_pros_obj.remove_ascending_trendlines(new_trendline_df)
            trend_existing_df = trend_existing_df.append(new_trendline_df)
            trend_existing_df = trendline_pros_obj.remove_duplicate_trendlines(trend_existing_df)
            # no new trendlines to add
            if existing_df_len == len(trend_existing_df) or len(trend_existing_df) == 0: continue

            trend_existing_df.sort_values(by="t_start", inplace=True)

            if trend_df_exists:
                trend_db_obj.update_data(trend_file_name, trend_existing_df, keep_old=False)
            else:
                trend_db_obj.add_data(list_ticker_names[index], trend_existing_df)

            self.process_lock.acquire()
            print(f"Processed trendlines on -> {list_ticker_names[index]}")
            self.process_lock.release()

    '''
    params:
        list_ticker_names -> list of tickers that need to be processed (TICKERS NOT FILE NAMES!)
        kwargs -> multiple -> pt.1 of key composition for needed dir
                  timespan -> pt.2 of key composition for needed dir
                  n_prev -> get_length_from_prev_local_extrema() params -> which low to measure from

        adds latest pole length to each trendline
    '''
    def add_pole_length(self, list_ticker_names, list_increment : mp.Value, **kwargs):

        # init db objects and verify that the directories exist 
        multiple, timespan, n_prev = kwargs['multiple'], kwargs['timespan'], kwargs['n_prev']  
        try:
            dir_params = str(multiple) + " " + timespan
            dir_list = popular_paths[f'historical {dir_params}']['dir_list']
            raw_data_obj = DataFlatDB(dir_list)
            needed_suf = raw_data_obj.suffix

            dir_list = popular_paths[f'bull triangles {dir_params}']['dir_list']
            trend_db_obj = DataFlatDB(dir_list)
        except:
            error_statement = f"Wrong directory parameters {dir_params}" 
            raise ValueError(error_statement)

        # create a list of files names 
        list_raw_ticker_file_names = [ticker + needed_suf for ticker in list_ticker_names]
        # exit when the shared memory variable reaches the end
        while list_increment.value != len(list_raw_ticker_file_names) - 1:
            with list_increment.get_lock():
                list_increment.value += 1
            index = list_increment.value
            file_name = list_raw_ticker_file_names[index]
            if index % 100 == 0 and index != 0:
                self.process_lock.acquire()
                print(f"Process identified extrema on {index} tickers")
                self.process_lock.release()
            # retrieve raw price data
            raw_df = raw_data_obj.retrieve_data(file_name)
            if len(raw_df) == 0: continue

            # determine the starting index
            trend_file_name = list_ticker_names[index] + trend_db_obj.suffix
            trend_existing_df = pd.DataFrame()
            trend_df_exists = trend_db_obj.verify_path_existence(trend_file_name)
            if not trend_df_exists:  continue
            trend_existing_df = trend_db_obj.retrieve_data(trend_file_name)

            trendline_feature_obj = TrendlineFeatureDesign()
            trend_existing_df[f"pole_length_{n_prev}"] = trendline_feature_obj.get_length_from_prev_local_extrema(
                                                                    endpoint_series=trend_existing_df["t_start"], 
                                                                    raw_price=raw_df,
                                                                    n_prev=n_prev,
                                                                    type_start_extrema="l",
                                                                    distance=5
                                                                    )

            trend_db_obj.update_data(trend_file_name, trend_existing_df, keep_old=False)




    '''
    params:
        proc_function -> specifies the function in this class you want to work on
        partial_fun_params -> dictionary that contains anything but the ticker list (kwargs)
        list_raw_ticker_file_names -> list of file names of raw prices fetched 
                                      (could be different each time, either all or only current)

    this function parallalizes the workload on the save_extrema_on_tickers() function by splitting
    up the work

    '''
    def parallel_ticker_workload(self, proc_function, partial_fun_params:dict, list_ticker_names:list):

        list_increment = mp.Value('i', -1) # I increment by 1 at the start of the loop in process function
        processes = []
        for i in range(TOTAL_PROCESSES):
            p = mp.Process(target=proc_function, args=(list_ticker_names, list_increment), kwargs=partial_fun_params)
            p.daemon = True # kills this child process if the main program exits
            processes.append(p)
        [x.start() for x in processes]
        [x.join() for x in processes]

    