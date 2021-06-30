# using yfinance to retrieve daily OHLC candles from Yahoo
import yfinance as yf
from yfinance import ticker

# using to access file
import pandas as pd
import os


# retrieving specified ticker with default range as 2020
# save to avoid ovearhead downloading it
def retrieve_ticker_data(ticker_id, start="2020-01-01", end="2020-12-30"):
    file_path = "/data/{}_{}_{}.csv".format(ticker_id, start, end)
    file_path = os.getcwd() + file_path 

    # check existing
    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path, index_col="Date")
        existing_df.index = pd.to_datetime(existing_df.index)
        return existing_df

    data = yf.download(ticker_id, start=start, end=end)
    data.to_csv(file_path)
    return data