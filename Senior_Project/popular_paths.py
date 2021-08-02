# available paths to copy into DataFlatDB constructor
popular_paths = {
    'historical 1 week' : {"dir_list" : ["data", "raw", "price", "1_week"], "params" : {"multiplier": 1, "timespan" : "week"}},
    'historical 1 day'  : {"dir_list" : ["data", "raw", "price", "1_day"],  "params" : {"multiplier": 1, "timespan" : "day"} },
    'current tickers'   : {"dir_list" : ["data", "watchlists", "current_tickers"] },
    'delisted tickers'  : {"dir_list" : ["data", "watchlists", "delisted_tickers"]}
}