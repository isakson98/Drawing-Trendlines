# using to access file
import pandas as pd
import os
import datetime as dt

# for faster data downloading
from concurrent.futures import ThreadPoolExecutor
import threading

# requests to exchanges
from StockScreener import StockScreener

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

class DataReceiveExtractor:

    dirname = os.path.dirname(__file__)
    raw_price_path =  os.path.join(dirname, "data\\raw\\price")
    processed_price_path = os.path.join(dirname, "data\\processed\\price")
    watchlists_path = os.path.join(dirname, "data\\watchlists")

    '''
    parameters: 
        recency -> how many days from today until prev ticker list is too old

    Use a library to fetch all existing tickers on top US exchanges
    Current stocks from: NYSE, NASDAQ, AMEX, no spacs, no tickers with 0 volume for that day

    Function gets new list of tickers if there is no previous record or prev file is too old
    '''
    def get_current_tickers(self, recency=10):
        file_name = "all_current_tickers.csv"
        file_path = os.path.join(self.watchlists_path, file_name)
        get_new_list = True
        if os.path.exists(file_path):
            timestamp_creation = os.stat(file_path).st_ctime
            creation_date = dt.datetime.fromtimestamp(timestamp_creation)
            today = dt.datetime.now()
            # if file was created more ago than preferred, rename file
            if today > creation_date + dt.timedelta(days=recency):
                new_file_name = creation_date.strftime("%d %B, %Y")
                updated_path = os.path.join(self.watchlists_path, new_file_name)
                os.rename(file_path, updated_path)
            else:
                get_new_list = False
                tickers = pd.read_csv(file_path)
            
        # if prev list file is too old or non existent, fetch a new one
        if get_new_list:
            screener = StockScreener()
            tickers = screener.retrieve_current_tickers()
            tickers.to_csv(file_path, index=False)

        return tickers["symbol"].tolist()

    '''
    using alpha vantage client library to get data
    alpha vantage has different endpoint for intaday and daily data
    naming standard -> ex. "TICKER_timeframe.csv" -> "AMC_d.csv"
    '''
    def get_price_data(self, ticker_name, timeframe="d"):

        # organize path
        ticker_name = ticker_name.upper()
        file_name = ticker_name + "_d.csv"
        file_path = os.path.join(self.raw_price_path, timeframe)
        file_path = os.path.join(file_path, file_name)

        # check existing
        if os.path.exists(file_path):
            print(f"{ticker_name} already downloaded")
            existing_df = pd.read_csv(file_path)
            existing_df["date"] = pd.to_datetime(existing_df["date"])
            return existing_df

        # TODO: download data here
        
        data.to_csv(file_path)
        data = data.reset_index()
        return data


    '''
    thread helper function for get_multiple_price_data()
    '''
    def __thread_get_multiple_price_data(self, list_tickers, timeframe="d"):
        
        data_list = dict()
        for ticker in list_tickers:
            data_list[ticker] = self.get_price_data(ticker, timeframe)
        return data_list
 

    '''
    function to use if you want to retrieve data from more than one stock
    each thread works on a section of the list that needs to be downloaded
    '''
    def get_multiple_price_data(self, list_tickers, timeframe="d", return_data=True, number_threads=10):
        
        if len(list_tickers) < number_threads:
            number_threads = len(list_tickers)

        portion_tickers = len(list_tickers) // number_threads

        list_threads = list()

        # split up the work evenly among threads
        # TODO -> use threadpoolexecutor to retrieve data and deal nicely with joins
        for thread in range(number_threads):
            start_ind = thread * portion_tickers
            end_ind = (1 + thread) * portion_tickers
            if thread == number_threads - 1:
                end_ind = len(list_tickers) - 1
            t = threading.Thread(
                                 target=self.__thread_get_multiple_price_data, 
                                 args=(list_tickers[start_ind:end_ind], timeframe,)
                                 )
            list_threads.append(t)
            t.start()

        # need to call join with this setup
        for thread in list_threads:
            thread.join()
        
        # return data_list
        

    '''
    this function can be used for the initial startup of the project
    '''
    def get_all_current_price_data(self, number_threads=10):
        all_current_stocks = self.get_current_tickers()
        self.get_multiple_price_data(all_current_stocks)
    
    '''
    use yfinance api
    keep track of current stocks
    '''
    def update_price_data(self, ticker):
        pass
    
    def get_fundies_data(self):
        pass

    def update_fundies_data(self):
        pass
