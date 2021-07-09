
from DataExtract import retrieve_ticker_data

# this library is 
# https://towardsdatascience.com/programmatic-identification-of-support-resistance-trend-lines-with-python-d797a4a90530
from trendln import plot_support_resistance

import matplotlib.pyplot as plt

ohlc_data = retrieve_ticker_data("TSLA")

fig = plot_support_resistance(ohlc_data["High"], accuracy=2, errpct=0.05, numbest=5)
print(fig.figure)
plt.show()