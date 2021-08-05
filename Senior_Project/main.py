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
from DataBase.popular_paths import popular_paths
from DataBase.FlatDBmodification import FlatDBmodification
from DataBase.DataFlatDB import DataFlatDB
from DataBase.StockScreener import ScreenerProcessor

# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import random

# retrieve daily candles for all current tickers
refresh_obj = FlatDBmodification()
params = popular_paths['historical 1 day']["params"]
dir_list = popular_paths['historical 1 day']["dir_list"]
refresh_obj.threaded_add_new_price_data(dir_list, params, update=True)





