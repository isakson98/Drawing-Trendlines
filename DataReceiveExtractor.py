# using yfinance to retrieve daily OHLC candles from Yahoo
import yfinance as yf
from yfinance import ticker

# using to access file
import pandas as pd
import os

# for faster data downloading
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
    raw_price_path =  os.path.join(dirname, "data\\raw")
    processed_price_path = os.path.join(dirname, "data\\processed")
    watchlists_path = os.path.join(dirname, "data\\watchlists")

    '''
    Use a library to fetch all existing tickers on top US exchanges
    Current stocks from: NYSE, NASDAQ, AMEX
    '''
    def get_current_tickers(self):
        # retrieve current tickers
        # importing only for this function because it has overhead
        file_name = "all_current_tickers.csv"
        file_path = os.path.join(self.watchlists_path, file_name)
        if os.path.exists(file_path):
            tickers = pd.read_csv(file_path)
            return tickers

        screener = StockScreener()
        tickers = screener.get_current_tickers()
        tickers.to_csv(file_path)
        return tickers

    '''
    use quandl or eodhistoricaldata api
    naming standard -> ex. "TICKER_timeframe.csv" -> "AMC_d.csv"
    valid timeframe: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    '''
    def get_price_data(self, ticker_name, timeframe="1d"):

        # organize path
        ticker_name = ticker_name.upper()
        file_name = ticker_name + "_" + timeframe
        file_path = os.path.join(self.raw_price_path, timeframe)
        file_path = os.path.join(file_path, file_name)

        # check existing
        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path, index_col="Date")
            existing_df.index = pd.to_datetime(existing_df.index)
            existing_df = existing_df.reset_index()
            return existing_df

        data = yf.download(ticker_name)
        data.to_csv(file_path)
        data = data.reset_index()
        return data

    '''
    function to use if you want to retrieve data from more than one stock
    '''
    def get_multiple_price_data(self, list_tickers, timeframe="1d", return_data=True, number_threads=10):
        # portion_tickers = len(list_tickers) // number_threads
        # for thread in range(number_threads):
        #     start_ind = thread * portion_tickers
        #     end_ind = (1 + thread) * portion_tickers
        #     if thread == number_threads - 1:
        #         end_ind = len(list_tickers) - 1
        #     t = threading.Thread(target=self.get_price_data, arg=(list_tickers[start_ind:end_ind]))

        data_list = dict()
        for ticker in list_tickers:
            data_list[ticker] = self.get_price_data(self, ticker, timeframe)

        return data_list
        

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





    # TODO -> think if you can implement a db with available stocks in it
    # consider how you want to structure it
    # do you want all stocks or only the best ones or best ones AND when they were trending?
    # TODO -> figure out the issue with dates and clipping portions of a stock for requested dates?
    '''
    retrieving specified ticker with default range as 2020 to present day
    save to avoid ovearhead downloading it
    '''
    def retrieve_ticker_data(self, ticker_id, start="2020-01-01", end="2021-07-15"):

        ticker_id = ticker_id.upper()
        file_path = "/data/{}_{}_{}.csv".format(ticker_id, start, end)
        file_path = os.getcwd() + file_path 

        # check existing
        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path, index_col="Date")
            existing_df.index = pd.to_datetime(existing_df.index)
            existing_df = existing_df.reset_index()
            return existing_df

        data = yf.download(ticker_id, start=start, end=end, threads=False)
        data.to_csv(file_path)
        data = data.reset_index()
        return data