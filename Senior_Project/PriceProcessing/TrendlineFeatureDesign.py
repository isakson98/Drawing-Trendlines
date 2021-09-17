
import pandas as pd
import multiprocessing as mp

'''

This class will cooperate significantly with two folders:
the trendlines AND the respective raw price where these trendlines were obtained from

'''
class TrendlineFeatureDesign:
    print_lock = mp.Lock()
    '''
    params:
        x -> current end point timestamp
        needed_raw_df -> only includes
        n_prev

    used by apply() in get_length_from_prev_local_extrema().

    HEAVILY USING THE INDEX -> make sure it's not modified in the future

    gets length from one local extrema to the other, including both extremas

    NOTE: in some rare cases, my start_extrema_index variable becomes None, so i will assign a negative value
    and then remove these rows during data processing.

    '''
    def __helper_len_from_local_extrema(self, x, needed_raw_df, starting_extrema_df, n_prev):
        # isolate the local start extrema index
        cut_off_timestamp_df = starting_extrema_df[starting_extrema_df["t"] < x]
        cut_off_extrema_df = cut_off_timestamp_df.tail(n_prev)
        start_extrema_index = cut_off_extrema_df.last_valid_index()
        if start_extrema_index == None: 
            start_extrema_index = -10000
            self.print_lock.acquire()
            print("negative pole length")
            self.print_lock.release()
        # get the end extrema's index
        end_of_pole_index_list = needed_raw_df.index[needed_raw_df["t"] == x].tolist()
        end_extrena_index = end_of_pole_index_list[0]
        # find the length of the original 
        rise_length = int(end_extrena_index - start_extrema_index) + 1
        return rise_length



    '''
    params:
        endpoint_series -> series that store the end point of the length (from trendline csv, start_timestamp column)
        raw_price -> raw price of the stock that will have lows 
        type_extrema -> 1st component of col that stores local extrema
                        either "h" or "l", meaning you want you length from local highs or lows
        distance -> 2nd component of column that stores local extrema
        n_prev -> which particular previous low you want the length to start from ()

    Many highs and lows have many trendlines coming out of them, but all of them essentially 
    will have the same output for this function if they share the same starting point.

    That's why I only calculate this feature on unique timestamps and then build up the original frequency count
    by merging 

    returns:
        series that match endpoint_series length, where each row corresponds to the same trendline in endpoint_series

    '''
    def get_pole_length(self, endpoint_series : pd.Series, raw_price, n_prev, type_start_extrema, distance):
        
        extrema_col_name = "_".join([type_start_extrema, "extremes", str(distance)])
        if extrema_col_name not in raw_price:
            print("No extrema column in raw data")
            return pd.Series()

        # condense original to include only rows that are extremas that we want
        starting_extrema_df = raw_price.loc[raw_price[extrema_col_name] == True]
        # condense condensed df to include only specified extrema and timestamp columns
        needed_raw_df = starting_extrema_df[[extrema_col_name, "t"]]

        # get only unique end point values 
        unique_endpoints = pd.Series(endpoint_series.unique())
        unique_df = pd.DataFrame({"unique_endpoints":unique_endpoints})
        unique_df["pole_length"] = unique_endpoints.apply(self.__helper_len_from_local_extrema, args=(raw_price,
                                                                                                      needed_raw_df, 
                                                                                                      n_prev))

        # match the unique values to the same column length and frequency of endpoints as the input
        match_length_df = pd.DataFrame({"endpoint" : endpoint_series})
        match_length_df = pd.merge(left=match_length_df, 
                                   right=unique_df,
                                   left_on="endpoint", 
                                   right_on="unique_endpoints", 
                                   how="left")
        
        return match_length_df["pole_length"]

    '''
    params:

    uses two columns the length of the consolidation (the flag) and 
    the length of the pole (from local low to trendline's peak)

    returns:

    '''
    def get_pole_to_flag_height_ratio(self):
        pass

    '''
    params:

    calculates the percentage of the rise since the last local low until price peaks

    returns:
    
    '''
    def get_pole_height(self):
        pass
        




        

