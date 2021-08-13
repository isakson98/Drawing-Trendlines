
import pandas as pd
import numpy as np
import concurrent.futures
from  random import shuffle
from functools import partial
import multiprocessing as mp

from DataBase.DataFlatDB import DataFlatDB
from DataBase.popular_paths import popular_paths
from PriceProcessing.TickerProcessing import TickerProcessing

'''

This class allows to perform modifications of data in the processed
section of the database.

Since it deals with processing files, a cpu-intensive task, instead of
utilizing threads like FlatDBRawMod class did, this class is going to use
processes instead.

'''
class FlatDBProssesedMod:

    printing_lock = mp.Lock()

    ################################################################################
                        # PROCESSED PRICE MANIPULATION # (MULTI - PROCESSED)
    ################################################################################
    '''
    params:
        multiple -> a number that is an aggregate of a timespan 
        timespan -> minute / hour / day / week / month (multiple and timespan params go together)
        distance -> # of candles that pass after extrema to consider it an extrema
        list_raw_ticker_file_names -> list of raw prices file names to read from
    
    create new files with highs and lows for all tickers (current and delisted)

    '''
    def save_extrema_on_tickers(self, multiple, timespan, distance, list_raw_ticker_file_names):
        # TODO -> think of how to to handle  timeframe access
        # determine 
        try:
            dir_params = str(multiple) + " " + timespan
            dir_list = popular_paths[f'historical {dir_params}']['dir_list']
            raw_data_obj = DataFlatDB(dir_list)
            dir_list = popular_paths[f'extrema {dir_params}']['dir_list']
            extreme_dir_obj = DataFlatDB(dir_list)
        except:
            error_statement = f"Wrong directory parameters {dir_params}" 
            raise ValueError(error_statement)

        for index, file_name in enumerate(list_raw_ticker_file_names):
            if index % 100 == 0 and index != 0:
                self.printing_lock.acquire()
                print(f"Process identified extrema on {index} tickers")
                self.printing_lock.release()
                
            # retrieve raw price data
            stock_df = raw_data_obj.retrieve_data(file_name)
            # verify processed file existence
            file_name_content = file_name.split("_")
            ticker_name = file_name_content[0]
            full_processed_file_name = ticker_name + extreme_dir_obj.suffix
            file_present = extreme_dir_obj.verify_path_existence(full_processed_file_name)

            # if processed file exists, append to the file, only examine last portion of
            if file_present:
                # get the date of the last extrema
                ticker_high_low_df = extreme_dir_obj.retrieve_data(full_processed_file_name)
                ticker_high_low_df_last_date = ticker_high_low_df.at[len(ticker_high_low_df)-1, "t"]
                # get the last piece of the raw data to find extrema in
                index_last_extrema_in_raw = stock_df[stock_df["t"] == ticker_high_low_df_last_date].index[0]
                piece_raw_to_process = stock_df.iloc[index_last_extrema_in_raw - distance*2:, :]
                piece_raw_to_process = piece_raw_to_process.reset_index()
                # find extrema
                processing_obj = TickerProcessing(piece_raw_to_process)
                new_lows_highs_df = processing_obj.identify_both_lows_highs(distance)
                # if there's no data to update, don't update anything
                if len(new_lows_highs_df) == 0:
                    continue
                # append to existing highs / lows
                both_old_new_extrema = pd.concat([ticker_high_low_df, new_lows_highs_df])
                extreme_dir_obj.update_data(ticker_name, both_old_new_extrema)
            else:
                # get lows and highs
                processing_obj = TickerProcessing(stock_df)
                high_low_df = processing_obj.identify_both_lows_highs(distance=distance)
                # dont save anything if there are no extremas to record
                if len(high_low_df) == 0:
                    continue
                # get ticker name to save data
                extreme_dir_obj.add_data(ticker_name, high_low_df)

    '''
    params:
        partial_fun_params -> dictionary that contains: multiple, timespan, distance keys
        list_raw_ticker_file_names -> list of file names of raw prices fetched 
                                      (could be different each time, either all or only current)
        n_core -> number of processes spawned during this function 

    this function parallalizes the workload on the save_extrema_on_tickers() function by splitting
    up the work

    '''
    def parallel_save_extrema(self, partial_fun_params, list_raw_ticker_file_names, n_core):
        # shuffle to distribute file sizes evenly
        shuffle(list_raw_ticker_file_names)
        ticker_pieces = np.array_split(list_raw_ticker_file_names, n_core)
        # “freezes” some portion of a function’s arguments and/or keywords resulting
        # in a new object with a simplified signature
        # apply_partial_extrema = partial(self.save_extrema_on_tickers, 
        #                         multiple=partial_fun_params["multiple"], 
        #                         timespan=partial_fun_params["timespan"],
        #                         distance=partial_fun_params["distance"])
        # apply_partial_extrema(list_raw_ticker_file_names=ticker_pieces[0])
        processes = []
        for i in range(n_core):
            p = mp.Process(target=self.save_extrema_on_tickers, args=(partial_fun_params["multiple"], 
                                                                      partial_fun_params["timespan"],
                                                                      partial_fun_params["distance"],
                                                                      ticker_pieces[i],))
            p.daemon = True # kills this child process if the main program exits
            processes.append(p)
        [x.start() for x in processes]
        [x.join() for x in processes]