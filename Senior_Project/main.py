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
# from DataBase.FlatDBmodification import FlatDBmodification
# from DataBase.StockScreener import ScreenerProcessor

# price processsing module
from PriceProcessing.TickerProcessing import TickerProcessing
from PriceProcessing.LinearRegTrendline import Trendline_Drawing
from PriceProcessing.Visualize import visualize_ticker

# robot made
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import random

TICKER = "goog"
TICKER.upper()

dir_list = popular_paths['historical 1 day']['dir_list']
data_getter = DataFlatDB(dir_list)
mrna_df = data_getter.retrieve_data(TICKER + data_getter.suffix)

mrna_df = mrna_df.iloc[-400:,]
mrna_df = mrna_df.reset_index()

processing_obj = TickerProcessing(mrna_df)
pross_mrna_df = processing_obj.identify_lows_highs(ohlc_type="h")

# total_lines = pd.DataFrame()
for i in range(4,16):
    trendline_obj = Trendline_Drawing(pross_mrna_df)
    lines_mrna_df = trendline_obj.identify_trendlines_LinReg(precisesness=i, max_trendlines_drawn=1)
    visualize_ticker(pross_mrna_df, additional_stuff=lines_mrna_df)
    # total_lines = total_lines.append(lines_mrna_df)
    print(f"done with {i}")








