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

# price processsing module
from PriceProcessing.RawPriceProcessing import RawPriceProcessing
from PriceProcessing.TrendlineDrawing import TrendlineDrawing
from PriceProcessing.Visualize import visualize_ticker

# popular scripts, combination of all modules features above
from CommonScripts import CommonScripts

# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd


if __name__ == '__main__':


    comm_obj = CommonScripts()
    # comm_obj.draw_descending_trendline_on_bullish_stock(STOCK_TO_VISUALIZE="FUTU")
    comm_obj.add_high_quality_higher_highs_daily(include_delisted=True, avg_v_min=50000)

    # visualize_ticker(ohlc_data=raw_df, peaks=highs_df)


    
