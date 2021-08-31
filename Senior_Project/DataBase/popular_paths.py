'''

popular_paths dictionary is available to quickly select
which directory you would like to work on, without having
to remember the exact path.

this also encourages the user to update the paths used only 
in one place if there is a shift in directories.

In addition to that, each path that gets original data from
a 3rd party source, like a Polygon REST API, has a "param" key
that specifies exactly which parameters are used in a call for this
particular directory. 

the rule is: 1 list of parameters PER directory (keeping things separate)

'''
popular_paths = {
    # MAKE SURE YOU ADJUST THE KEY NAME EVERYWHERE IF YOU DECIDE TO CHANGE THE KEY NAME

    ############################
    # RAW FOLDER
    ############################
    'historical 1 week' : {"dir_list" : ["data", "raw", "price", "1_week"], "params" : {"multiplier": 1, "timespan" : "week"}},
    'historical 1 day'  : {"dir_list" : ["data", "raw", "price", "1_day"],  "params" : {"multiplier": 1, "timespan" : "day"} },

    ############################
    # WATCHLIST FOLDER
    ############################
    'current tickers'   : {"dir_list" : ["data", "watchlists", "current_tickers"] },
    'delisted tickers'  : {"dir_list" : ["data", "watchlists", "delisted_tickers"]},

    ############################
    # PROCESSED FOLDER
    ############################
    'bull triangles 1 day' : {"dir_list" : ["data", "processed", "bullish_triangles"]}

}