# public modules
import pandas as pd
import datetime as dt
from polygon import RESTClient

# developed modules
from DataBase.credentials import polygon_key

'''
This class is a wrapper for the Polygon client library.
In my case, since I seek to have a full database, I want data
from the earliest event possible till today. 

It seems that I will keep on adding new methods as I will need
to use new API calls from the library. This is fine because I would
need to write code to add a new API call anyways. Except this time,
I am buidling same safety features as well as specifying exactly what kind
of certain parameters I want from the call.
'''
class DataDownload:

    '''
    params:
        ticker -> name of ticker you want data of
        multiplier -> aggregate window (ex. if 1 -> data per 1 minute/day/week)
        timespan -> timeframe (minute, hour, day, week, month, year)
        from_ -> timestamp or date (YYYY-MM-DD) that is starting point
        to -> timestamp or date (YYYY-MM-DD) that is the end point
    
    description:
        Wrapper for aggregate(bars) API call from Polygon
        By default, this function wants data from the earliest date possible till today

    returns:
        data -> DataFrame of received result (empty if no result)
    '''
    def dwn_price_data(self, ticker, multiplier, timespan, from_="1900-01-01", to=dt.date.today().strftime("%Y-%m-%d")):
        ticker = ticker.upper()
        data = pd.DataFrame()
        with RESTClient(polygon_key) as client:
            resp = client.stocks_equities_aggregates(ticker=ticker, 
                                                        multiplier=multiplier, 
                                                        timespan=timespan,
                                                        from_= from_,
                                                        to=to) 
            
            if resp.resultsCount > 0:
                data = pd.DataFrame(resp.results)
            return data


