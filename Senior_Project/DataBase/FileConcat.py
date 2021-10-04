

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
        path_to_save_in -> new directory to save in 
        file_name -> new file name to save as
    
    this file concatantes files in the given directory

    Whoa -> concat is silly fast
    
    '''

    def concat_files(self, path_to_save_in, file_name):
        
        all_file_names = self.retrieve_all_file_names()
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
        self.change_dir(path_to_save_in)
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
    def add_new_columns(file_to_add_to, dir_to_add_from, list_attribute_to_add):
        pass





