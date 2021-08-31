from random import shuffle
import numpy as np
import multiprocessing as mp
import pandas as pd
from pandas.core.frame import DataFrame

from PriceProcessing.TrendlineDrawing import TrendlineDrawing
from DataFlatDB import DataFlatDB
from popular_paths import popular_paths

TOTAL_PROCESSES = 5


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
        list_ticker_names -> list of tickers that need to be processed (TICKERS NOT FILE NAMES!)
        kwargs -> multiple -> pt.1 of key composition for needed dir
                  timespan -> pt.2 of key composition for needed dir
    '''
    def add_bullish_desc_trendlines(self, list_ticker_names, **kwargs):

        multiple, timespan = kwargs['multiple'], kwargs['timespan']
        # verify that the directories exist 
        try:
            dir_params = str(multiple) + " " + timespan
            dir_list = popular_paths[f'historical {dir_params}']['dir_list']
            raw_data_obj = DataFlatDB(dir_list)
            needed_suf = raw_data_obj.suffix

            trend_dir_list = popular_paths[f'bull triangles {dir_params}']['dir_list']
            trend_db_obj = DataFlatDB(trend_dir_list)
        except:
            error_statement = f"Wrong directory parameters {dir_params}" 
            raise ValueError(error_statement)

        # create a list of files names 
        list_raw_ticker_file_names = [ticker + needed_suf for ticker in list_ticker_names]
        # read each stock in a loop
        for index, file_name, in enumerate(list_raw_ticker_file_names):
            if index % 100 == 0 and index != 0:
                self.proc_lock.acquire()
                print(f"Process identified extrema on {index} tickers")
                self.proc_lock.release()
                
            # retrieve raw price data
            stock_df = raw_data_obj.retrieve_data(file_name)
            if len(stock_df) == 0:
                continue
            
            # identify where to start updating from
            hh_hq_t = stock_df["t"].loc[stock_df["hq_hh"]==True]
            # getting the index 
            hh_hq_index_list = hh_hq_t.index.tolist()
            trendline_obj = TrendlineDrawing(ohlc_raw=stock_df, start_points_list=hh_hq_index_list)

            preciseness = [2, 3, 4, 5, 6]
            trendlines_df = pd.DataFrame()
            for one_prec in preciseness:
                new_trendline_df = trendline_obj.identify_trendlines_LinReg(line_unit_col="h", preciseness=one_prec)
                trendlines_df.append(new_trendline_df)
            
            # prep trendlines dataframe 
            trendlines_df.sort_values(by="t", inplace=True)
            trend_file_name = list_ticker_names[index] + trend_db_obj.suffix
            trend_db_obj.update_data(trend_file_name, trendlines_df, keep_old=False)

        pass


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

    pass
    