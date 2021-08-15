'''

if new type of data arrives -> manually create a folder or reorganize stuff
then give the location to DataReceiveExtractor class

need some kind of structure that verifies the data directories


THIS OF THIS AS A CLIENT SPACE.
This is the researcher ground.
This is where you are going to request and write stuff and ask for analysis
Do not delegate everything to library classes, as this overfits stuff (no hard coding)


'''
# database module
from DataBase.popular_paths import popular_paths
from DataBase.DataFlatDB import DataFlatDB  
from DataBase.FlatDBRawMod import FlatDBRawMod  
from DataBase.FlatDBProssesedMod import FlatDBProssesedMod

# price processsing module
from PriceProcessing.TickerProcessing import TickerProcessing
from PriceProcessing.LinearRegTrendline import Trendline_Drawing
from PriceProcessing.Visualize import visualize_ticker

# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

#############################################################################   
# create new files with highs and lows for all tickers (current and delisted)
############################################################################# 

if __name__ == '__main__':

    STOCK_TO_VISUALIZE = "NUE"
    raw_obj = DataFlatDB(popular_paths["historical 1 day"]["dir_list"])
    raw_df = raw_obj.retrieve_data(STOCK_TO_VISUALIZE+raw_obj.suffix)

    extrema_obj = DataFlatDB(popular_paths["extrema 1 day"]["dir_list"])
    extrema_df = extrema_obj.retrieve_data(STOCK_TO_VISUALIZE+extrema_obj.suffix)

    tick_obj = TickerProcessing()
    higher_highs = tick_obj.get_higher_extrema(extrema_df, extrema="h", distance=5, above_last_num_highs=2)
    
    for prec in [2,3,4,5,6,7,8,9,10]:
        trendline_obj = Trendline_Drawing(raw_df, higher_highs, breakout_based_on="strong close")
        trendline_df = trendline_obj.identify_trendlines_LinReg(distance=5, 
                                                                extrema_type="h", 
                                                                precisesness=prec, 
                                                                max_trendlines_drawn=2)  

        desc_trendlines = trendline_obj.remove_ascending_trendlines(trendline_df)                                                        
        visualize_ticker(raw_df, higher_highs, desc_trendlines)

