'''

if new type of data arrives -> manually create a folder or reorganize stuff
then give the location to DataReceiveExtractor class

need some kind of structure that verifies the data directories


THIS OF THIS AS A CLIENT SPACE.
This is the researcher ground.
This is where you are going to request and write stuff and ask for analysis
Do not delegate everything to library classes, as this overfits stuff (no hard coding)


'''

if __name__ == '__main__':

    #############################################################################
    # man made
    from popular_paths import popular_paths
    from FlatDBmodification import FlatDBmodification

    # retrieve delisted tickers
    flat_ob = DataFlatDB(popular_paths["delisted tickers"]["dir_list"])
    delisted_df = flat_ob.retrieve_data("all_delisted_tickers.csv")

    # clean up file
    delisted_clean_up_obj = ScreenerProcessor()
    delisted_df = delisted_clean_up_obj.rmv_financial_instruments(delisted_df)
    delisted_df = delisted_clean_up_obj.rmv_spacs(delisted_df)
    delisted_df = delisted_clean_up_obj.rmv_subclass_shares(delisted_df)
    delisted_df = delisted_clean_up_obj.rmv_numbered_symbols(delisted_df)
    flat_ob.update_data("all_delisted_tickers.csv", content_to_add=delisted_df, keep_old=False)

    delisted_list = delisted_df["symbol"].tolist()

    #############################################################################

    # update current ticker csv and delisted csv
    refresh_obj = FlatDBmodification()
    refresh_obj.update_current_ticker_list()

    # retrieve data from
    refresh_obj = FlatDBmodification()
    params = popular_paths['historical 1 day']["params"]
    dir_list = popular_paths['historical 1 day']["dir_list"]
    refresh_obj.threaded_add_new_price_data(dir_list, params, update=False)

    amc_df = refresh_obj.re

    #############################################################################
    # ---------------------------- TRENDLINE MATERIAL --------------------------------- #

    from DataFlatDB import DataFlatDB
    from LinearReg_Trendline import Trendline_Drawing
    flat_ob = DataFlatDB()
    file_name = "AMC" + flat_ob.suffix
    amc_df = flat_ob.retrieve_data(file_name)

    trendline_obj = Trendline_Drawing(amc_df)
    touches = [2, 3, 4, 5 ]  # how many peaks ("touches") you want in a trendline (2 is minimumu)
    extrema_distance = 5
    trendline_length = 10
    trendlines_drawn = 1 # 1 provides cleaner results
    trendline_obj.identify_lows_highs(ohlc_type="High", distance=extrema_distance)
    for precisesness in touches:
        descending_df = trendline_obj.identify_trendlines_LinReg(extreme="High", 
                                                                min_days_out=trendline_length, 
                                                                precisesness=precisesness,
                                                                max_trendlines_drawn=trendlines_drawn)
        visualize_ticker(amc_df, descending_df)

