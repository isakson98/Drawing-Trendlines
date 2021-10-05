

from DataBase.DataFlatDB import DataFlatDB

import pandas as pd
import os

'''

This class is going to be used for concataneting 1000's of single stock files into one

Because this class will use heavily the capabilities of the core DataFlatDB class, 
I decided that this class will be a child of DataFlatDB

'''

class FileConcat(DataFlatDB):

    '''
    params:
        path_to_concat -> directory to pull data from
        file_name -> new file name to save as
    
    this file concatantes files in the given directory

    Whoa -> concat is silly fast    
    '''

    def concat_files(self, path_to_concat, file_name):
        
        concat_path = DataFlatDB(path_to_concat)

        all_file_names = concat_path.retrieve_all_file_names()
        df_list = []

        for index, file in enumerate(all_file_names):
            if index % 100 == 0 and index != 0: print(f"{index} added to list")

            # extract ticker data and add ticker column to it
            new_df = self.retrieve_data(file)
            ticker = self.parse_ticker_name(file)
            new_df["ticker"] = ticker
            df_list.append(new_df)

        
        print("Concataneting now")
        big_df = pd.concat(df_list)
        self.add_data(file_name, big_df)
        
    '''
    params:
        file_name -> file name
    purpose:
        extracting ticker name from the file name
    return:
        name of ticker -> string
    '''
    def parse_ticker_name(self, file_name : str):
        name_comp = file_name.split("_")
        return name_comp[0]


    counter = 0
    def __helper_add_new_columns(self, ticker_df : pd.DataFrame, new_data_db_obj : DataFlatDB, list_attribute_to_add :list):

        if self.counter % 100 == 0: print(f"{self.counter} added new col added")

        # extract the ticker of the group
        ticker = str(ticker_df.loc[ticker_df.index.values[0], "ticker"])
        # retrieve desired data
        df_to_add_from = new_data_db_obj.retrieve_data(ticker + new_data_db_obj.suffix)
        # retrieve only desired columns
        selected_cols_df = df_to_add_from[list_attribute_to_add]

        # merge on timestamps, merge only on what is currently avaiable.
        final_ticker_df = pd.merge(left=ticker_df,
                                    left_on="t_start",
                                    right=selected_cols_df,
                                    right_on="t",
                                    how="left")

        # dropping what we were merging on the right side
        final_ticker_df = final_ticker_df.drop("t", axis=1)

        self.counter += 1
        return final_ticker_df
        

    '''
    params:
        file_to_add_to
        dir_to_add_from
        list_attribute_to_add
    purpose:
        adding new columns to big file of tickers
    return:
        none
    '''
    def add_new_columns(self, file_to_add_to, dir_to_add_from, list_attribute_to_add):

        new_data_db_obj = DataFlatDB(dir_to_add_from)        
        big_data_df : pd.DataFrame = self.retrieve_data(file_to_add_to)

        # column to merge on
        list_attribute_to_add.extend("t")

        # groupsby by ticker and operates by each ticker
        new_big_df = big_data_df.groupby("ticker").apply(self.__helper_add_new_columns, new_data_db_obj, list_attribute_to_add)
        
        new_big_df = new_big_df.reset_index(drop=True)

        print("Writing to a file")

        self.update_data(file_to_add_to, new_big_df, keep_old=True)

