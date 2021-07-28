# using to access file
import pandas as pd
import os
import datetime as dt

# for faster data downloading
from concurrent.futures import ThreadPoolExecutor
import threading

# requests to exchanges
from StockScreener import NasdaqStockScreener

'''
-> DATA 
features / ideas:
--> use stock price data
--> feature / precomputed data from price or volume
--> data should be easily updateable 
----> on a daily basis
----> trendlines' labels (whether they worked or not) should be updateable based on entry and on exit spefications
q:
--> What medium do I use to store data? (csv, hdf5, relational db, etc.)
--> how do I store feature data like high and low that depend on parameters themselves? 
---> should I store these features under columns that specify which parameters are used?
--> how do I choose the parameters for highs / lows and linear regression quality to capture all possible versions of successful trendlines
raw data where I got a trendline from should be easily accessible to add features for the neural network
'''

'''
Objectives:
- get daily price data from Quandl (interaction with Quandl API)
- be able to retrieve portions of data and apply filters for scanning purposes (different class)
- be able to update prices for those tickers that are still public (interaction with yfinance)
- be able to obtain price data as well as fundumental (some other api)
'''


'''
This class deals with the database of the project

if any type of file needs to be either created / deleted / modified, this is the go to class

implementations of retrieving data from any kind of api will be found in other files, classes

this class takes care of
- managing files in proper directories

'''
# TODO: find a way to deal with directory structures and concotonating file paths gracefully
class DataManager:

    dirname = os.path.dirname(__file__)
    raw_price_path =  os.path.join(dirname, "data\\raw\\price")
    processed_price_path = os.path.join(dirname, "data\\processed\\price")
    watchlists_path = os.path.join(dirname, "data\\watchlists")

    screener = NasdaqStockScreener()

    '''
    params
        file_path -> path to file to be renamed

    this function is used when a new version of data is available,
    but the old one is decided to be saved as well. Use this function
    to add date to the outdated file, so as to show that it is an old file
    '''
    def __add_date_to_file_name(self, file_path):
        directory, file_name =  os.path.split(file_path)
        _, str_date = self.__get_files_creation_date(file_path)
        new_file_name = str_date + "_" + file_name 
        updated_path = os.path.join(directory, new_file_name)
        
        if os.path.exists(updated_path) == False:
            os.rename(file_path, updated_path)

        return updated_path

    '''
    helper function that fetches the creation date of the file

    returns 
        creation_date -> datetime object of the date
        string_v -> string version of the date for adding to file name
    '''
    def __get_files_creation_date(self, path):

        timestamp_creation = os.stat(path).st_ctime
        creation_date = dt.datetime.fromtimestamp(timestamp_creation)
        string_v = creation_date.strftime("%d-%b-%Y")
        print(string_v)
        return creation_date, string_v

    '''
    parameters: 
        recency -> how many days from today until prev ticker list is too old
        force -> when you force to get a new list from the API, regardless of the recency (used when updating)

    Use a library to fetch all existing tickers on top US exchanges
    Current stocks from: NYSE, NASDAQ, AMEX, no spacs, no tickers with 0 volume for that day

    Function gets new list of tickers if there is no previous record or prev file is too old
    '''
    def get_current_tickers(self, recency=10, force=False):
        current_tix_file_name = "all_current_tickers.csv"
        current_tix_path = os.path.join(self.watchlists_path, "current_tickers")
        current_tix_path = os.path.join(current_tix_path, current_tix_file_name)
        get_new_list = True

        new_tickers = pd.DataFrame()
        if os.path.exists(current_tix_path):
            creation_date, _ = self.__get_files_creation_date(current_tix_path)
            today = dt.datetime.now()

            # if file was created more ago than preferred, 
            # rename file to show that it is old
            if today > creation_date + dt.timedelta(days=recency) or force:
                outdated_tickers = pd.read_csv(current_tix_path)
                self.__add_date_to_file_name(current_tix_path)
            else:
                get_new_list = False
                new_tickers = pd.read_csv(current_tix_path)
            
        # if prev list file is too old or non existent, fetch a new one
        # or retrieve forcefully
        # also update delisted ticker files if necessary
        if get_new_list or force:
            new_tickers = self.screener.retrieve_current_tickers()
            new_tickers.to_csv(current_tix_path, index=False)

            delisted_file = "all_delisted_tickers.csv"
            deslisted_tix_path = os.path.join(self.watchlists_path, "delisted_tickers")
            deslisted_tix_path = os.path.join(deslisted_tix_path, delisted_file)
            delisted_tickers = pd.read_csv(deslisted_tix_path)
            
            new_delisted_tickers = self.screener.update_delisted_stocks(delisted_tickers, outdated_tickers, new_tickers)
        
            if len(new_delisted_tickers) > 0:
                self.__add_date_to_file_name(deslisted_tix_path)
                new_delisted_tickers.to_csv(deslisted_tix_path, index=False)

        return new_tickers["symbol"].tolist()

    '''
    params:
        ticker_name -> ticker to fetch the data of
        params -> parameters used for the api call
        update -> True if you want to get the most recent data

    Using Polygon client library to get data
    Naming standard -> ex. "TICKER_timeframe.csv" -> "AMC_d.csv"
    '''
    # instead of timeframe as parameter, think of using a container "params"
    # TODO: make this compatible with update
    # what can go into params -> timeframe="d", from="", to="",
    def get_price_data(self, ticker_name, params, update=False):

        # organize path
        ticker_name = ticker_name.upper()
        file_name = ticker_name + "_" + params["timeframe"] + ".csv"
        file_path = os.path.join(self.raw_price_path, params["timeframe"])
        file_path = os.path.join(file_path, file_name)

        # check existing
        if os.path.exists(file_path):
            print(f"{ticker_name} already downloaded")
            data = pd.read_csv(file_path)
            data["date"] = pd.to_datetime(data["date"])
            if update:
                data["date"]
            return data
        
        if update or not os.path.exists(file_path) :
            # TODO: download data here
            data.to_csv(file_path)
            data = data.reset_index()

        return data


    '''
    params:
        list_tickers -> a segment of tickers, alloted to a particular thread

    thread helper function for get_multiple_price_data()
    
    '''
    def __thread_get_multiple_price_data(self, list_tickers, params):
        
        data_list = dict()
        for ticker in list_tickers:
            data_list[ticker] = self.get_price_data(ticker, params)
        return data_list
 

    '''
    function to use if you want to retrieve data from more than one stock
    each thread works on a section of the list that needs to be downloaded
    '''
    def get_multiple_price_data(self, list_tickers, params={"timeframe":"d"}, number_threads=10):
        
        # in case there are less ticker symbols than threads given
        if len(list_tickers) < number_threads:
            number_threads = len(list_tickers)
        portion_tickers = len(list_tickers) // number_threads

        # split up the work evenly among threads
        # TODO -> use threadpoolexecutor to retrieve data and deal nicely with joins
        list_threads = list()
        for thread in range(number_threads):

            # assign start and end indices of the list to a specific thread
            start_ind = thread * portion_tickers
            end_ind = (1 + thread) * portion_tickers
            if thread == number_threads - 1:
                end_ind = len(list_tickers) - 1

            t = threading.Thread(
                                 target=self.__thread_get_multiple_price_data, 
                                 args=(list_tickers[start_ind:end_ind], params)
                                 )
            list_threads.append(t)
            t.start()

        # wait for threads to finish
        for thread in list_threads:
            thread.join()
                

    '''
    this function can be used for the initial startup of the project
    '''
    def get_all_current_price_data(self, number_threads=10, force=False):
        all_current_stocks = self.get_current_tickers(force=force)
        self.get_multiple_price_data(all_current_stocks)
    
    '''
    updating price data also involves knowing which stocks are actually still current
    after finding which stocks are current, this function find the last date on file
    and appends newly retrieved data for the file
    '''
    def update_price_data(self, ticker):
        all_current_stocks = self.get_current_tickers(force=True)
        self.get_multiple_price_data(all_current_stocks)
        pass
    
    def get_fundies_data(self):
        pass

    def update_fundies_data(self):
        pass
