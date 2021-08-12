
from math import floor
import pandas as pd
import numpy as np
import threading
import datetime as dt

from DataBase.DataFlatDB import DataFlatDB
from DataBase.DataDownload import DataDownload
from DataBase.popular_paths import popular_paths
from DataBase.StockScreener import NasdaqStockScreener

TOTAL_THREADS = 10

'''
This class will be used for common DB modifications
'''
class FlatDBRawMod:

    flat_db = None
    current_df = None
    lock = threading.Lock()
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
        # TODO -> use threadpoolexecutor to retrieve data and deal nicely with joins
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
                self.lock.acquire()
                print(f"{index} tickers processed by a thread")  
                self.lock.release()  

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
