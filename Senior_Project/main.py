'''

if new type of data arrives -> manually create a folder or reorganize stuff
then give the location to DataReceiveExtractor class

need some kind of structure that verifies the data directories


THIS OF THIS AS A CLIENT SPACE.
This is the researcher ground.
This is where you are going to request and write stuff and ask for analysis
Do not delegate everything to library classes, as this overfits stuff (no hard coding)


'''
# man made
from popular_paths import popular_paths
from FlatDBmodification import FlatDBmodification
from DataFlatDB import DataFlatDB
from StockScreener import ScreenerProcessor

# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import random

# retrieve delisted tickers
flat_ob = DataFlatDB(popular_paths["delisted tickers"]["dir_list"])
delisted_df = flat_ob.retrieve_data("all_delisted_tickers.csv")
delisted_list = delisted_df["symbol"].tolist()

# list in ascending order time wise, so first thread will get most available tickers
# this mixes it up 
random.shuffle(delisted_list)

# download data for delisted tickers
dir_list = popular_paths["historical 1 day"]["dir_list"]
params = popular_paths["historical 1 day"]["params"]
flat_mod = FlatDBmodification()
flat_mod.threaded_add_new_price_data(dir_list=dir_list, 
                                     params=params, 
                                     update=False, 
                                     tickers_to_update=delisted_list)





