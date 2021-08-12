
import pandas as pd

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

    ################################################################################
                        # PROCESSED PRICE MANIPULATION # (MULTI - PROCESSED)
    ################################################################################
    '''
    params:
        distance -> 
    
    create new files with highs and lows for all tickers (current and delisted)

    '''
    def find_extrema_on_existing_ticker(self, multiple, timespan, distance, list_raw_ticker_file_names):
        # TODO -> think of how to to handle timeframe access

        dir_list = popular_paths['historical 1 day']['dir_list']
        raw_data_obj = DataFlatDB(dir_list)

        dir_list = popular_paths['extrema 1 day']['dir_list']
        extreme_dir_obj = DataFlatDB(dir_list)

        list_raw_ticker_file_names = raw_data_obj.retrieve_all_file_names()
        # TODO -> check if file exists
        for index, file_name in enumerate(list_raw_ticker_file_names):
            if index % 100 == 0:
                print(f"Process identified extrema on {index} tickers")
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