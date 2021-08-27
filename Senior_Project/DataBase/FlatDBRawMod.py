
from math import floor
import pandas as pd
import numpy as np
import threading
import multiprocessing
import datetime as dt
import multiprocessing as mp
from  random import shuffle



from DataBase.DataFlatDB import DataFlatDB
from DataBase.DataDownload import DataDownload
from DataBase.popular_paths import popular_paths
from DataBase.StockScreener import NasdaqStockScreener

from PriceProcessing.RawPriceProcessing import RawPriceProcessing

TOTAL_THREADS = 5
# TEMP
TOTAL_PROCESSES = 1

# turning off the warning
pd.options.mode.chained_assignment = None  # default='warn'

'''

This class will be used for common DB modifications in the RAW sub-folder

It utilizes either threads or processess for concurrency, depending on the task.
It always accepts a list of tickers as a parameter (not the file name) and then 
attaches the file name


'''
class FlatDBRawMod:

    flat_db = None
    current_df = None
    thread_lock = threading.Lock()
    proc_lock = multiprocessing.Lock()

    ticker_proc_obj = RawPriceProcessing()

    # by default, i am assuming I am going to deal with current tickers
    # likely to change, but that's what I am staying with for now
    def __init__(self):
        self.flat_db = DataFlatDB(popular_paths["current tickers"]["dir_list"])
        self.current_df = self.flat_db.retrieve_data("all_current_tickers.csv")

    '''
    update_current_ticker_list() updates a file of current tickes by utilizing
    a NasdaqStockScreener() object, which makes a call to scrape Nasdaq's screener page.
    In addition to that, this function compares the refresh list of tickers and adds outdated
    tickers to the delisted file in another directory.
    '''
    def update_current_ticker_list(self):
        self.flat_db = DataFlatDB(popular_paths["current tickers"]["dir_list"])
        current_tix_file_name = "all_current_tickers.csv"
        prev_current_df = self.flat_db.retrieve_data(current_tix_file_name)

        nsdq_screener = NasdaqStockScreener()
        new_df = nsdq_screener.retrieve_current_tickers()

        delisted_file_name = "all_delisted_tickers.csv"
        delisted_file_db = DataFlatDB(popular_paths["delisted tickers"]["dir_list"])
        delisted_df = delisted_file_db.retrieve_data(delisted_file_name)

        new_delisted_df = nsdq_screener.update_delisted_stocks(delisted_df, prev_current_df, new_df)

        if len(new_delisted_df) > 0:
            delisted_file_db.update_data(delisted_file_name, new_delisted_df, keep_old=True)

        self.flat_db.update_data(current_tix_file_name, new_df, keep_old=True)

        return new_delisted_df
    
    '''
    params:
        dir_list -> top-down list of dirs to the final one, where you want to update
        params -> list of parameters for the Polygon API call
        tickers_to_update -> empty by default, specific list of tickers you want to update
    
    populate_price_directory() responsible for creating new files (single threaded)
    '''
    def populate_price_directory(self, dir_list, params, list_of_tickers=[]):
        self.flat_db.change_dir(dir_list)
        if len(list_of_tickers) == 0:
            list_of_tickers = self.current_df["symbol"].tolist()

        downloader = DataDownload()
        for ticker in list_of_tickers:
            new_df = downloader.dwn_price_data(ticker=ticker,
                                            multiplier=params["multiplier"],
                                            timespan=params['timespan'])
            if len(new_df) > 0:
                self.flat_db.add_data(ticker, new_df)
    
    '''
    params:
        dir_list -> top-down list of dirs to the final one, where you want to update
        params -> list of parameters for the Polygon API call
                  multiplier 
                  timespan
        tickers_to_update -> empty by default, specific list of tickers you want to update
    
    refresh_directory() -> connects two modules DataFlatDB (os wrapper) and DataDownload to update
    existing files with the freshest dates (single threaded)
    '''
    def refresh_price_directory(self, dir_list, params, tickers_to_update=[]):
        self.flat_db.change_dir(dir_list)
        dir_suffix = self.flat_db.suffix
        if len(tickers_to_update) == 0:
            tickers_to_update = self.current_df["symbol"].tolist()

        downloader = DataDownload()
        for index, ticker in enumerate(tickers_to_update):
            if index % 100 == 0:
                print(f"{index} tickers processed by a thread")  

            full_file_name = ticker + dir_suffix
            price_df = self.flat_db.retrieve_data(full_file_name)
            last_time = price_df.at[len(price_df)-1, "t"]
            new_df = downloader.dwn_price_data(ticker=ticker,
                                            multiplier=params["multiplier"],
                                            timespan=params['timespan'],
                                            from_ = last_time)

            if len(new_df) > 1:
                # drop first row, since it is the same one as the last row in original df
                new_df.drop(new_df.head(1).index,inplace=True)            
                updated_df = pd.concat([price_df, new_df])
                self.flat_db.update_data(full_file_name, updated_df, keep_old=False)

    ################################################################################
                        # RAW PRICE MANIPULATION # (threaded)
    ################################################################################

    '''
    params:
        dir_list -> top-down list of dirs to the final one, where you want to update
        params -> list of parameters for the Polygon API call
        update -> whether you want to update or populate from fresh
        tickers_to_update -> empty by default, specific list of tickers you want to update

     threaded_add_new_data deals 
    '''
    def threaded_add_new_price_data(self, dir_list, params, update, tickers_to_update=[]):

        # change directory to where you will operate on
        self.flat_db.change_dir(dir_list)

        # if no tickers are given, get the freshest ones available
        if len(tickers_to_update) == 0:
            tickers_to_update = self.current_df["symbol"].tolist()

        global TOTAL_THREADS
        # in case there are less ticker symbols than threads given
        if len(tickers_to_update) < TOTAL_THREADS:
            TOTAL_THREADS = len(tickers_to_update)
        portion_tickers = len(tickers_to_update) // TOTAL_THREADS

        # split up the work evenly among threads
        list_threads = list()
        for thread in range(TOTAL_THREADS):

            # assign start and end indices of the list to a specific thread
            start_ind = thread * portion_tickers
            end_ind = (1 + thread) * portion_tickers
            if thread == TOTAL_THREADS - 1:
                end_ind = len(tickers_to_update) - 1

            t = threading.Thread(
                                 target=self.__thread_dwn_multiple_price_data, 
                                 args=(tickers_to_update[start_ind:end_ind], params, update)
                                 )
            list_threads.append(t)
            t.start()

        # wait for threads to finish
        for thread in list_threads:
            thread.join()

    '''
    params:
        list_tickers -> a segment of tickers, alloted to a particular thread
        params -> getting passed down from a few functions above, params for the Polygon API call
        update -> whether we are adding values to existing tickers or nah

    thread helper function for get_multiple_price_data()
    IMPORTANT to note that we are adding name key to the params dictionary here.
    Otherwise, get_price_data() will fail without having a string ticker as a param 
    
    '''
    def __thread_dwn_multiple_price_data(self, list_tickers, params, update):
        dir_suffix = self.flat_db.suffix


        downloader = DataDownload()
        for index, ticker in enumerate(list_tickers):

            if index % 100 == 0:
                self.thread_lock.acquire()
                print(f"{index} tickers processed by a thread")  
                self.thread_lock.release()  

            to_stamp = self.__choose_final_timestamp()
            full_file_name = ticker + dir_suffix

            # if updating file, retrieve its content and get last row's time
            if update:
                price_df = self.flat_db.retrieve_data(full_file_name)
                # ticker is in list of current tickers, but not in flat DB yet (new ticker)
                if len(price_df) == 0:
                    last_time = "1900-01-01"
                else:
                    last_time = price_df.at[len(price_df)-1, "t"] # returns milliseconds
                    # avoid making a request if data is completely recent
                    if last_time >= to_stamp:
                        continue   
            
            # if not updating
            if not update:
                file_exists = self.flat_db.verify_path_existence(full_file_name)
                if file_exists:
                    continue
                last_time = "1900-01-01"

            # download the data
            new_df = downloader.dwn_price_data(ticker=ticker,
                                            multiplier=params["multiplier"],
                                            timespan=params['timespan'],
                                            from_=last_time,
                                            to=to_stamp
                                            )

            # if we received some data, save it to the file
            # think of repurcussions for this
            if len(new_df) > 1 :
                if last_time != "1900-01-01":
                    # drop first row, since it is the same one as the last row in original df
                    new_df.drop(new_df.head(1).index,inplace=True)            
                    updated_df = pd.concat([price_df, new_df])
                    self.flat_db.update_data(full_file_name, updated_df, keep_old=False)
                elif last_time == "1900-01-01":
                    self.flat_db.add_data(ticker, new_df)

    '''
    params:
        today_datetime -> displays current time

    this function is used to determine where to cap the data arrival
    I do not want to receive incomplete data for todays date in the
    middle of the day

    returns:
        timestamp in milliseconds of the last bar to fetch
    
    '''
    def __choose_final_timestamp(self):

        today_datetime = dt.datetime.now()
        str_today = today_datetime.strftime("%Y-%m-%d")
        final_mili_timestamp = 0
        # if weekend can pull until todays date
        if not np.is_busday(str_today):
            final_mili_timestamp = today_datetime.timestamp() 
        else:
            if today_datetime.hour >= 20:
                final_mili_timestamp = today_datetime.timestamp() 
            else:
                yesterday = today_datetime - dt.timedelta(days=1)
                yesterday = yesterday.replace(hour = 0)
                yesterday = yesterday.replace(minute = 0)
                yesterday = yesterday.replace(second = 0)
                final_mili_timestamp = yesterday.timestamp() 

        final_mili_timestamp = floor(final_mili_timestamp)
        return int(final_mili_timestamp * 1000)

    '''
    params:
        list_ticker_names -> list of tickers that need to be processed (TICKERS NOT FILE NAMES!)

        **kwargs -> multiple, timespan, distance
            multiple -> a number that is an aggregate of a timespan 
            timespan -> minute / hour / day / week / month (multiple and timespan params go together)
            distance -> # of candles that pass after extrema to consider it an extrema

    important to note: this function looks up the proper directory of the files, based 
    on the timespan and the multiple, that are components of a key in the dict in popular_paths.py

    can be launched by parallel_ticker_workload()
    
    create new files with highs and lows for all tickers (current and delisted)

    '''
    def add_freshest_extrema_on_tickers(self, list_ticker_names, **kwargs):
        multiple, timespan, distance = kwargs['multiple'], kwargs['timespan'], kwargs['distance']
        # verify that the directories exist 
        try:
            dir_params = str(multiple) + " " + timespan
            dir_list = popular_paths[f'historical {dir_params}']['dir_list']
            raw_data_obj = DataFlatDB(dir_list)
            needed_suf = raw_data_obj.suffix
        except:
            error_statement = f"Wrong directory parameters {dir_params}" 
            raise ValueError(error_statement)

        # create a list of files names 
        list_raw_ticker_file_names = [ticker + needed_suf for ticker in list_ticker_names]

        processing_obj = RawPriceProcessing()
        for index, file_name in enumerate(list_raw_ticker_file_names):
            if index % 100 == 0 and index != 0:
                self.proc_lock.acquire()
                print(f"Process identified extrema on {index} tickers")
                self.proc_lock.release()
                
            # retrieve raw price data
            stock_df = raw_data_obj.retrieve_data(file_name)
            if len(stock_df) == 0:
                continue

            extrema_h_col = f"h_extremes_{distance}"
            extrema_l_col = f"l_extremes_{distance}"

            # if processed file exists, append to the file, only examine last portion of it
            if extrema_h_col in stock_df.columns or extrema_l_col in stock_df.columns:
                # get the date of the last extrema
                # find the last element volume row where there is a value
                index = pd.isna(stock_df[extrema_h_col])
                empty = index[index==True]
                # fresh data -> no changes needed
                if len(empty) == 0:
                    continue
                empty = empty.index.tolist()
                first_empty_extrema = empty[0]
                # get the last piece of the raw data to find extrema in
                piece_raw_to_process = stock_df.iloc[first_empty_extrema - distance*2:, :]
                piece_raw_to_process = piece_raw_to_process.reset_index()
                # find extrema
                extrema_dict = processing_obj.get_both_lows_highs(series_high = piece_raw_to_process['h'], 
                                                                       series_low  = piece_raw_to_process['l'],
                                                                       distance    = distance)
                # if there's no data to update, don't update anything
                if len(extrema_dict["high"]) == 0:
                    continue
                stock_df[extrema_h_col].iloc[first_empty_extrema- distance*2:] = extrema_dict["high"]
                stock_df[extrema_l_col].iloc[first_empty_extrema- distance*2:] = extrema_dict["low"]
                # append to existing highs / lows
                raw_data_obj.update_data(file_name, stock_df, keep_old=False)
            # process entire new 
            else:
                # get lows and highs
                extrema_dict = processing_obj.get_both_lows_highs(series_high=stock_df['h'],
                                                                       series_low =stock_df['l'],
                                                                       distance=distance)
                stock_df[extrema_h_col] = extrema_dict["high"]
                stock_df[extrema_l_col] = extrema_dict["low"]
                # dont save anything if there are no extremas to record
                if len(stock_df) == 0:
                    continue

                # get ticker name to save data
                raw_data_obj.update_data(file_name, stock_df, keep_old=False)

    '''
    params:
        list_ticker_names -> list of tickers that need to be processed (TICKERS NOT FILE NAMES!)
        kwargs -> multiple, 
                  timespan, 
                  days_window
    
    this function adds freshest average volume 

    important to note: this function looks up the proper directory of the files, based 
    on the timespan and the multiple, that are components of a key in the dict in popular_paths.py

    can be launched by parallel_ticker_workload()
    
    '''
    def add_freshest_average_volume(self, list_ticker_names, **kwargs):

        # unpacking key word arguments
        multiple, timespan, candle_window = kwargs["multiple"], kwargs["timespan"], kwargs["candle_window"]

       # verify that the directories exist 
        try:
            dir_params = str(multiple) + " " + timespan
            dir_list = popular_paths[f'historical {dir_params}']['dir_list']
            raw_data_obj = DataFlatDB(dir_list)
            needed_suf = raw_data_obj.suffix
        except:
            error_statement = f"Wrong directory parameters {dir_params}" 
            raise ValueError(error_statement)

        # create a list of files names 
        list_raw_ticker_file_names = [ticker + needed_suf for ticker in list_ticker_names]

        processing_obj = RawPriceProcessing()
        for index, file_name in enumerate(list_raw_ticker_file_names):
            if index % 100 == 0 and index != 0:
                self.proc_lock.acquire()
                print(f"Process identified extrema on {index} tickers")
                self.proc_lock.release()
                
            # retrieve raw price data
            stock_df = raw_data_obj.retrieve_data(file_name)

            avg_vol_col_name = f"avg_v_{candle_window}"

            # if processed file exists, append to the file, only examine last portion of it
            if avg_vol_col_name in stock_df.columns:
                # find the last element volume row where there is a value
                index = pd.isna(stock_df[f"avg_v_{candle_window}"].loc[candle_window:])
                empty = index[index==True]
                # fresh data no changes needed
                if len(empty) == 0:
                    continue
                empty = empty.index.tolist()
                first_empty_avg_vol = empty[0] 
                # get a copy of n-last rows before it
                vol_series = stock_df["v"].iloc[first_empty_avg_vol - candle_window + 1:]
                # get avg vol for entire column
                avg_vol_series = processing_obj.get_average_volume(vol_series, candle_window)
                # attach new series to old ones
                stock_df[f"avg_v_{candle_window}"].iloc[first_empty_avg_vol:] = avg_vol_series.loc[first_empty_avg_vol:]
                # get ticker name to save data
                raw_data_obj.update_data(file_name, stock_df, keep_old=False)

            # process entire new 
            else:
                # get avg vol for entire column
                try:
                    stock_df[avg_vol_col_name] = processing_obj.get_average_volume(stock_df["v"], candle_window)
                except:
                    self.proc_lock.acquire()
                    print(f"issues calculating volume in {file_name}")
                    self.proc_lock.release()
                # get ticker name to save data
                raw_data_obj.update_data(file_name, stock_df, keep_old=False)
    '''
    params:
        list_ticker_names -> list of tickers that need to be processed (TICKERS NOT FILE NAMES!)
        kwargs -> multiple
                  timespan
                  extrema_distance
                  avg_v_distance
                  avg_v_min

    this function creates/updates a column named "hq_hh" -> high quality higher highs
    these are higher highs, filtered further by average volume at the extrema
    
    '''
    def add_high_qual_higher_highs(self, list_ticker_names, **kwargs):

        # unpacking key word arguments
        multiple, timespan, extrema_distance, avg_v_distance, avg_v_min = kwargs.values()

       # verify that the directories exist 
        try:
            dir_params = str(multiple) + " " + timespan
            dir_list = popular_paths[f'historical {dir_params}']['dir_list']
            raw_data_obj = DataFlatDB(dir_list)
            needed_suf = raw_data_obj.suffix
        except:
            error_statement = f"Wrong directory parameters {dir_params}" 
            raise ValueError(error_statement)

        # create a list of files names 
        list_raw_ticker_file_names = [ticker + needed_suf for ticker in list_ticker_names]

        for index, file_name in enumerate(list_raw_ticker_file_names):
            if index % 100 == 0 and index != 0:
                self.proc_lock.acquire()
                print(f"Process identified extrema on {index} tickers")
                self.proc_lock.release()
                
            # retrieve raw price data
            stock_df = raw_data_obj.retrieve_data(file_name)

            tick_obj = RawPriceProcessing()

            # get higher highs
            # above_last_num_highs param hardcoded in both functions cause I already experimented with these values
            higher_highs = tick_obj.get_higher_extrema(stock_df, extrema="h", distance=extrema_distance, above_last_num_highs=2)
            # get highs that are higher than previous higher highs
            higher_highs = tick_obj.get_higher_extrema(higher_highs, extrema="h", distance=extrema_distance, above_last_num_highs=1)
            # filter further by volume
            higher_highs = higher_highs[higher_highs[f"avg_v_{avg_v_distance}"] > avg_v_min]

            # merge on all same columns
            # if "on" absent merges on intersection
            stock_df = pd.merge(left=stock_df, right=higher_highs, how="left")

            print(stock_df.tail(20))

            # get ticker name to save data
            # raw_data_obj.update_data(file_name, stock_df, keep_old=False)

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
        # shuffle to distribute file sizes evenly
        shuffle(list_ticker_names)
        ticker_pieces = np.array_split(list_ticker_names, TOTAL_PROCESSES)
        processes = []
        for i in range(TOTAL_PROCESSES):
            p = mp.Process(target=proc_function, args=(ticker_pieces[i],), kwargs=partial_fun_params)
            p.daemon = True # kills this child process if the main program exits
            processes.append(p)
        [x.start() for x in processes]
        [x.join() for x in processes]


