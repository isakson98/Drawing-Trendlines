
import pandas as pd
import multiprocessing as mp

'''

This class will cooperate significantly with two folders:
the trendlines AND the respective raw price where these trendlines were obtained from

'''
class TrendlineFeatureDesign:
    new_raw_price_df = None
    print_lock = mp.Lock()
    '''
    params:
        x -> current end point timestamp
        needed_raw_df -> only includes
        n_prev

    purpose: 
        used by apply() in get_length_from_prev_local_extrema().

        HEAVILY USING THE INDEX -> make sure it's not modified in the future

        gets length from one local extrema to the other, including both extremas

        NOTE: in some rare cases, my start_extrema_index variable becomes None, so i will assign a negative value
        and then remove these rows during data processing.

    return:
        int value for the column of the respective row 

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

    purpose: 
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
        flag_length -> computed during trendline detection
        pole_length -> computed in self.get_pole_length(...)

    purpose: 
        uses two columns the length of the consolidation (the flag) and 
        the length of the pole (from local low to trendline's peak). This demonstrates
        how much of a "break" is needed for a successful stock to start moving higher again.

    returns: a series that is ratio of pole length to flag length

    '''
    def get_pole_to_flag_length_ratio(self, pole_length, flag_length):
        return pole_length / flag_length


    '''
    params:
        flag_start -> starting timestamp
        flag_end -> ending timsetamp of the trendline

    purpose: 
        getting the timestamp of the flag low (used as intermediary value)

        NOTE: used by apply() in get_flag_low_timestamp 

    returns: 
        the timestamp of low

    '''
    def __helper_flag_low_timestamp(self, flag_start, flag_end):
        short_raw_df = self.new_raw_price_df[(self.new_raw_price_df["t"] >= flag_start) & (self.new_raw_price_df["t"] <= flag_end)]
        low_timestamp = short_raw_df["t"].loc[short_raw_df["l"].idxmin()]
        return low_timestamp
    
    '''
    params:
        raw_df -> raw price df of the stock
        trend_existing_df -> df with trendline features and other info

    purpose: 
        getting the timestamp of the flag low (used as intermediary value)

    returns: 
        a series that is ratio of pole length to flag length

    '''
    def get_flag_low_timestamp(self, trend_existing_df, raw_price):
        
        self.new_raw_price_df = raw_price
        flag_low_tmstmp_series = trend_existing_df.apply(lambda row : self.__helper_flag_low_timestamp(
                                                                                                 row["t_start"],
                                                                                                 row["t_end"], 
                                                                                                 ), axis =1)                                                                                       

        return flag_low_tmstmp_series

    '''
    params:
        tmstmp -> timestamp at which the low is

    purpose:
        helper row function that gets price low from raw_df for 
        NOTE: used by apply() in get_flag_low_price

    return:
        low of the flag for repsective row
    '''
    def __helper_flag_low_price(self, tmstmp):
        # get the low of timestamp that is given from the trendline
        low_value = self.new_raw_price_df['l'].loc[self.new_raw_price_df["t"] == tmstmp]
        return float(low_value)


    '''
    params:
        raw_df -> raw price df of the stock
        trend_existing_df -> df with trendline features and other info

    returns: a series that has a flag low price for the given row trendline

    '''
    def get_flag_low_price(self, trendline_df, raw_price_df):

        self.new_raw_price_df = raw_price_df
        flag_low_tmstp_series = trendline_df["flag_low_timestamp"]

        # get only unique end point values 
        unique_tmstp = pd.Series(flag_low_tmstp_series.unique())
        unique_df = pd.DataFrame({"unique_flag_low_tmstmp":unique_tmstp})
        unique_df["flag_low_price"] = unique_tmstp.apply(self.__helper_flag_low_price)

        # match the unique values to the same column length and frequency of endpoints as the input
        match_length_df = pd.DataFrame({"flag_low_timestamp" : flag_low_tmstp_series})
        match_length_df = pd.merge(left=match_length_df, 
                                   right=unique_df,
                                   left_on="flag_low_timestamp", 
                                   right_on="unique_flag_low_tmstmp", 
                                   how="left")
        
        return match_length_df["flag_low_price"]


    '''
    params:
        flag_start -> timsetamp of flag start
        flag_low_t -> timsetamp of flag low
        flag_end -> timestamp of flag end

    purpose:
        applies row wise operation of getting the flag low
        perhaps a more efficient way would be to check wehther there is
        a weekend in between and subtract that from the length
        instead of applying inquality operation each time

        NOTE: used by apply() method in get_flag_low_progress()

    return:
        progress ratio value
    
    '''
    def __helper_flag_low_progress(self, flag_start, flag_low_t, flag_end):
        # find the length of the whole consolidation
        short_raw_df = self.new_raw_price_df[(self.new_raw_price_df["t"] >= flag_start) & (self.new_raw_price_df["t"] <= flag_end)]
        total_length = len(short_raw_df)
        # find the length of consolidation before the low, including the low
        progress_len = len(short_raw_df[short_raw_df["t"] <= flag_low_t])
        # get the ratio of low location in the progreess over entire consolidation
        progress = progress_len / total_length

        return progress

    '''
    params:
        raw_price_df -> raw price df of the stock
        trend_existing_df -> df with trendline features and other info

    purpose:
        caclculates the ratio of where the low of the flag is relative to the length of it

        NOTE: ends inclusive (includes the breakout day and the first day of flag as well)

    returns:    
        a series that shows the progress at which the flag bottomed.

    '''
    def get_flag_low_progress(self, trendline_df, raw_price_df):

        self.new_raw_price_df = raw_price_df  
        flag_low_progress_series = trendline_df.apply(lambda row : self.__helper_flag_low_progress( row["t_start"],
                                                                                                 row["flag_low_timestamp"],
                                                                                                 row["t_end"], 
                                                                                                 ), axis =1)

        return flag_low_progress_series

    '''
    params:
        raw_df -> raw price df of the stock
        trend_existing_df -> df with trendline features and other info

    purpose:
        this ratio shows the pivot price relative to the flags low. 

    returns
        a series that shows the ratio between the peak - pivot price range and peak - low price range.
    
    '''
    def get_pivot_flag_height_ratio(self, price_start_series:pd.Series, price_flag_low_series, price_end_series):

        total_height = price_start_series - price_flag_low_series
        peak_pivot_range = price_start_series - price_end_series
        needed_ratio = peak_pivot_range / total_height

        return needed_ratio


    '''
    params:
        x -> 
        starting_extrema_df -> start of extrema 
        n_prev

    purpose:
        NOTE: rare error TypeError: cannot convert the series to <class 'int'>
        replacing it negative number to exclude these later

    return:
        timestamp of when the pole started (its lows essentially)
    
    '''
    def __helper_get_pole_start_timestamp(self, x, starting_extrema_df, n_prev):
        # isolate the local start extrema index
        cut_off_timestamp_df = starting_extrema_df[starting_extrema_df["t"] < x]
        cut_off_extrema_df = cut_off_timestamp_df.tail(n_prev)
        try:
            timestamp_of_pole_start = int(cut_off_extrema_df["t"].head(1))
        except:
            timestamp_of_pole_start = -1
        return timestamp_of_pole_start


    '''
    params:
        raw_price_df -> raw price df of the stock
        trendlines_df -> df with trendline features and other info

    purpose:
        calculates a series that shows the timestamp of a pole start (as specified which local low)
        for every trendline in trendline df. This is a useful starting measure for further data extraction
        about that timestamp.

    returns: 
        a series that shows the timestamp of a pole start 

    '''
    
    def get_pole_start_timestamp(self, endpoint_series, raw_price, n_prev, type_start_extrema, distance):
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
        unique_df["pole_start_timestamp"] = unique_endpoints.apply(self.__helper_get_pole_start_timestamp, args=(needed_raw_df, 
                                                                                                                 n_prev))

        # match the unique values to the same column length and frequency of endpoints as the input
        match_length_df = pd.DataFrame({"endpoint" : endpoint_series})
        match_length_df = pd.merge(left=match_length_df, 
                                   right=unique_df,
                                   left_on="endpoint", 
                                   right_on="unique_endpoints", 
                                   how="left")
        
        return match_length_df["pole_start_timestamp"]

    '''
    params:
        raw_price_df -> raw price df of the stock
        trendlines_df -> df with trendline features and other info
    
    purpose: 
        this function retrieves the prices of lows of the given pole

    returns: 
        a series of lows at the timestamp given.
    '''
    def get_pole_start_price(self, trend_existing_df, raw_price):        

        merge_df =  pd.merge(left=trend_existing_df["pole_start_timestamp"], 
                             left_on = trend_existing_df["pole_start_timestamp"],
                             right=raw_price,
                             right_on="t",
                             how="left")
        
        return merge_df["l"]

    
    '''
    purpose:
        row_timestamp_pole_low
        raw_price

    purpose:
        used by apply() in get_pole_height_in_candles

    returns:
        float value of the last few candles' average true
    
    '''
    LAST_N_ROWS = 20
    def __helper_get_pole_height_in_candles(self, row_timestamp_pole_low, raw_price):
        
        last_n_df = raw_price[raw_price["t"] < row_timestamp_pole_low].tail(self.LAST_N_ROWS)
        last_n_df_range = last_n_df["h"] - last_n_df["l"]
        last_n_average_range = last_n_df_range.sum() / self.LAST_N_ROWS

        return last_n_average_range


    '''
    params:
        raw_price_df -> raw price df of the stock
        trendlines_df -> df with trendline features and other info
    
    purpose: 
        to give some context to the model with regards to the pole height,
        i want it to be measured with respect to the last n days before the start of the pole.
        i want the pole to be measured in number of n previous average candles' heights.
        ex. 3 previous candles before pole start have ranges(difference between height and low): 1.5, 2.5, 2
        average range is (1.5 + 2.5 + 2)/3 = 2 dollars per day. Let's say pole height is 20 dollars up
        that means the pole height is 20 / 2 = 10 average candles. 

    returns: 
        a series of pole height in previous candle
    '''
    def get_pole_height_in_candles(self, trend_existing_df, raw_price):

        if "pole_start_price" not in trend_existing_df:
            trend_existing_df[ "pole_start_price" ] = self.get_pole_start_price(trend_existing_df, raw_price)

        # NOTE: hardcoding this name
        extrema_col_name = "l_extremes_5"
        if extrema_col_name not in raw_price:
            raise ValueError("No extrema column in raw data")

        pole_start_tmstp_series = trend_existing_df["pole_start_timestamp"]

        # get only unique end point values  -> calculate their range
        unique_pole_start_tmstp_series = pd.Series(pole_start_tmstp_series.unique())
        unique_df = pd.DataFrame({"unique_endpoints":unique_pole_start_tmstp_series})
        unique_df["average_range"] = unique_pole_start_tmstp_series.apply(self.__helper_get_pole_height_in_candles, args=(raw_price,))

        # match the unique values to the same column length and frequency of endpoints as the input
        match_length_df = pd.DataFrame({"endpoint" : pole_start_tmstp_series})
        match_length_df = pd.merge(left=match_length_df, 
                                   right=unique_df,
                                   left_on="endpoint", 
                                   right_on="unique_endpoints", 
                                   how="left")

        
        # calculate the height of the pole in terms of the average range
        pole_height_in_terms_of_average_range = (trend_existing_df["price_start"] - trend_existing_df["pole_start_price"]) / match_length_df["average_range"]

        return pole_height_in_terms_of_average_range


    '''
    params:
        trendlines_df -> df with trendline features and other info
        raw_df -> i do not need this for this function explicitly, but incase
                  i have to calculate pre existing columns
    
    purpose: 
        to give some persepctive on how well the flag is holding, i will 
        calculate the ratio of pole's vertical range and the flag's vertical range.

        NOTE: it's POLE / FLAG ratio (pole comes first)

    returns: 
        a series of ratios that correspond to each row (a trendline row)
    '''  
    def get_pole_flag_height_ratio(self, trendlines_df, raw_df):

        if "flag_low_price" not in trendlines_df:
            trendlines_df["flag_low_price"] = self.get_flag_low_price(trendlines_df, raw_df)
        if "pole_start_price" not in trendlines_df:
            trendlines_df["pole_start_price"] = self.get_pole_start_price(trendlines_df, raw_df)
        
        pole_range = trendlines_df["price_start"] - trendlines_df["pole_start_price"]
        flag_range = trendlines_df["price_start"] - trendlines_df["flag_low_price"]

        return pole_range / flag_range


        

        






        




        

