

from DataFlatDB import DataFlatDB
from DataDownload import DataDownload
from popular_paths import popular_paths

import pandas as pd

'''
This class will be used for common DB modifications
'''
class FlatDBmodification:

    flat_db = None
    current_df = None
    # by default, i am assuming I am going to deal with current tickers
    # likely to change, but that's what I am staying with for now
    def __init__(self):
        self.flat_db = DataFlatDB(popular_paths["current tickers"])
        self.current_df = self.flat_db.retrieve_data("all_current_tickers.csv")

    '''
    retrieves 
    '''
    def update_current_ticker_list(self):
        pass
    
    '''
    params:
        dir_list -> top-down list of dirs to the final one, where you want to update
        params -> list of parameters for the Polygon API call
        tickers_to_update -> empty by default, specific list of tickers you want to update
    refresh_directory()
    connects two modules DataFlatDB (os wrapper) and 
    
    TODO:one caveat with the current method: there is no verfication
        that you are downloading the right thing into the right folder
        should extension match the folder?
        should I take the name of the extension based on existing files in the folder?
    '''
    def refresh_price_directory(self, dir_list, params, tickers_to_update=[]):
        self.flat_db.change_dir(dir_list)
        dir_suffix = self.flat_db.suffix
        if len(tickers_to_update) == 0:
            tickers_to_update = self.current_df["symbol"].tolist()

        downloader = DataDownload()
        for ticker in tickers_to_update:
            full_file_name = ticker + dir_suffix
            price_df = self.flat_db.retrieve_data(full_file_name)
            last_time = price_df.at[-1, "t"]
            new_df = downloader.dwn_price_data(ticker=ticker,
                                            multiplier=params["multiplier"],
                                            timespan=params['timespan'],
                                            from_ = last_time)
            # drop first row, since it is the same one as the last row in original df
            new_df.drop(new_df.head(1).index,inplace=True)            
            updated_df = pd.concat([price_df, new_df])

            self.flat_db.update_data(full_file_name, updated_df, keep_old=False)
