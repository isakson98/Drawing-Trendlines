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

# popular scripts, combination of all modules features above
from CommonScripts import CommonScripts

# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd


if __name__ == '__main__':

    common_obj = CommonScripts()
    common_obj.add_latest_avg_vol_to_raw_daily()
    
