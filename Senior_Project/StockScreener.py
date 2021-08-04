import pandas as pd
from enum import Enum
import io
import requests
import datetime


'''
ScreenerProcessor class used to clean up lists of stocks 

This is used now to clean up incoming data from the Nasdaq API call
and to clean delisted stocks.
'''
class ScreenerProcessor:
    '''
    parameter -> cur_tickers_df (must contain column "symbol")
    this function filters out rows where a symbol has "." in it,
    like BRK.A or BRK.B

    Reason: these are difficult to clean up
    '''
    def rmv_subclass_shares(self, cur_tickers_df):
        df_filtered = cur_tickers_df[~cur_tickers_df['symbol'].str.contains("\.|\^|\/|\-")]
        return df_filtered

    '''
    parameter -> cur_tickers_df (must contain column "symbol")
    this function filters out rows where a symbol has a number
    at the end of it

    Reason: these are difficult to clean up
    '''
    def rmv_numbered_symbols(self, cur_tickers_df):
        df_filtered = cur_tickers_df[~cur_tickers_df['symbol'].str.contains(r'\d')]
        return df_filtered

    '''
    parameter -> cur_tickers_df (must contain column "name")
    this function filters out rows where a name has "Acquisition" in it

    Reason: acquisition implies this is a SPAC, which usually do not follow
    technical analysis well (when they hover around 10 dollars without momentum)
    This function also removes warrants.
    '''
    def rmv_spacs(self, tickers_df):
        tickers_df = tickers_df[~tickers_df['name'].str.contains("acquisition", case=False, regex=False)]
        return tickers_df

    '''
    parameter -> cur_tickers_df (must contain column "name")
    this function filters out rows where a name has "Acquisition" in it

    Reason: similar reason to spacs, these are repetitive instruments
    '''
    def rmv_financial_instruments(self, tickers_df):
        tickers_df = tickers_df[~tickers_df['name'].str.contains("index", case=False, regex=False)]
        tickers_df= tickers_df[~tickers_df['name'].str.contains("trust", case=False, regex=False)]
        tickers_df= tickers_df[~tickers_df['name'].str.contains("etf", case=False, regex=False)]
        tickers_df = tickers_df[~tickers_df['name'].str.contains("etn", case=False, regex=False)]
        tickers_df = tickers_df[~tickers_df['name'].str.contains("fund", case=False, regex=False)]
        tickers_df = tickers_df[~tickers_df['name'].str.contains("holdings", case=False, regex=False)]
        tickers_df = tickers_df[~tickers_df['name'].str.contains("capital", case=False, regex=False)]
        tickers_df = tickers_df[~tickers_df['name'].str.contains("bear|bull", case=False, regex=False)]
        tickers_df = tickers_df[~tickers_df['name'].str.contains("direxion|proshares|oppenheimer", case=False, regex=False)]

        return tickers_df

    '''
    parameter -> cur_tickers_df (must contain column "volume")
    this function filters out rows where volume is 0.

    Reason: these are warrants and greatly unnecessary tickers.
    '''
    def rmv_empty_volume(self, tickers_df):
        tickers_df = tickers_df[tickers_df["volume"] > 0]
        return tickers_df


'''
This class retrieves stock data from Nasdaq's API

TODO: it will also be able to apply different other kinds of filters
based on sector, industry, marketcap, a combo of these, etc

Although it is possible to filter using Nasdaq's API as well,
it is slow, limited in options of filtering available, and unreliable,
as they can shut down the access to the api or modify it's html structure

it is a child class of stock screener

'''
class NasdaqStockScreener(ScreenerProcessor):
    
    _EXCHANGE_LIST = ['nyse', 'nasdaq', 'amex']

    headers = {
        'authority': 'api.nasdaq.com',
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'origin': 'https://www.nasdaq.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.nasdaq.com/',
        'accept-language': 'en-US,en;q=0.9',
    }

    tickers_df = pd.DataFrame()
    
    def params(self, exchange):
        return (
            ('tableonly', 'true'),
            ('limit', '25'),
            ('offset', '0'),
            ('download', 'true'),
            ('exchange', exchange)
        )

    '''
    central function of the class
    it fetches data from NASDAQ api, given the parameters
    '''
    def retrieve_current_tickers(self, NYSE=True, NASDAQ=True, AMEX=True, SPACS=False, CLASS_SHARES=False):

        exchange_dict = {'nyse':NYSE, 'nasdaq':NASDAQ, 'amex':AMEX}
        for exchange in self._EXCHANGE_LIST:
            if exchange_dict[exchange]:
                cur_exch_tickers_df = self.__fetch_from_exchange(exchange)
                self.tickers_df = pd.concat([self.tickers_df, cur_exch_tickers_df])

        self.tickers_df = self.__clean_up_api_return_df(self.tickers_df )

        if CLASS_SHARES == False:
            self.tickers_df = self.rmv_subclass_shares(self.tickers_df)

        if SPACS == False:
            self.tickers_df = self.rmv_spacs(self.tickers_df)

        # self.tickers_df = self.rmv_empty_volume(self.tickers_df)

        return self.tickers_df

    '''
    params
        exchange -> specifying which exchange to get stocks from

    Given the exchange as the parameter,
    This function makes an API call to NASDAQ database to retrieve stocks from the underlying exchange

    returns a DataFrame of stocks and their info
    '''
    def __fetch_from_exchange(self, exchange):
        param_list = self.params(exchange)
        r = requests.get('https://api.nasdaq.com/api/screener/stocks', headers=self.headers, params=param_list)
        data = r.json()['data']
        df = pd.DataFrame(data['rows'], columns=data['headers'])
        return df

    '''
    params 
        ticker_df -> dataframe that needs to be cleaned up

    the official data from NASDAQ is messy, there are symbols, and numbers are strings.
    this function fixes that, as well as replaces empty cells and nans with 0
    '''
    def __clean_up_api_return_df(self, ticker_df):
        # remove signs from columns
        ticker_df["lastsale"] = ticker_df["lastsale"].map(lambda x: x.lstrip("$"))
        ticker_df["pctchange"] = ticker_df["pctchange"].map(lambda x: x.rstrip("%"))

        columns_that_need_float = ["lastsale", "netchange", "pctchange", "marketCap"]
        dict_to_float = {column : 'float64' for column in columns_that_need_float}
        columns_that_need_int = ["ipoyear", "volume"]
        dict_to_int = {column : 'int64' for column in columns_that_need_int}

        all_cols_wit_nums = columns_that_need_float.extend(columns_that_need_int)
        ticker_df.replace(to_replace=[None], value=0, inplace=True)
        ticker_df.replace(to_replace=[""], value=0, inplace=True)

        # converting given columns to ints or floats
        ticker_df = ticker_df.astype(dict_to_float)
        ticker_df = ticker_df.astype(dict_to_int)

        # remove spaces in symbol names (saw it a couple of times)
        ticker_df["symbol"] = ticker_df["symbol"].str.strip()
   

        return ticker_df

    
    
    '''
    params
        delisted_tickers -> from the delisted folder
        outdated_tickers -> from the old current_tickers file
        new_tickers -> from the newly fetched API call

    returns
        delisted_tickers -> updated df with delisted stocks
    '''
    def update_delisted_stocks(self, delisted_tickers, outdated_tickers, new_tickers):
        outdate_list = outdated_tickers["symbol"].tolist()
        new_list = new_tickers["symbol"].tolist()
        # find difference between new and outdated tickers
        old_stocks = list(set(outdate_list) - set(new_list))

        # no new tickers found
        if len(old_stocks) == 0:
            return old_stocks

        new_old_stocks_df = outdated_tickers[outdated_tickers["symbol"].isin(old_stocks)]
        new_old_stocks_df["date"] = datetime.date.today()

        # make it compatible with delisted tickers
        delisted_tickers = pd.concat([delisted_tickers, new_old_stocks_df])

        return delisted_tickers 


    def filter_by_marketcap(self, lower_limit, upper_limit):
        pass

    def filter_by_region(self, region):
        pass

    def filter_by_sector(self, sector):
        pass



if __name__ == '__main__':

    screener_obj = NasdaqStockScreener()

    df = screener_obj.retrieve_current_tickers()
    print(df.head(10))

#     tickers = get_tickers()
#     print(tickers[:5])

#     tickers = get_tickers(AMEX=False)

#     # default filename is tickers.csv, to specify, add argument filename='yourfilename.csv'
#     save_tickers()

#     # save tickers from NYSE and AMEX only
#     save_tickers(NASDAQ=False)

#     # get tickers from Asia
#     tickers_asia = get_tickers_by_region(Region.ASIA)
#     print(tickers_asia[:5])

#     # save tickers from Europe
#     save_tickers_by_region(Region.EUROPE, filename='EU_tickers.csv')

#     # get tickers filtered by market cap (in millions)
#     filtered_tickers = get_tickers_by_market_cap(mktcap_min=500, mktcap_max=2000)
#     print(filtered_tickers[:5])

#     # not setting max will get stocks with $2000 million market cap and up.
#     filtered_tickers = get_tickers_by_market_cap(mktcap_min=2000)
#     print(filtered_tickers[:5])

#     # get tickers filtered by sector
#     filtered_by_sector = get_tickers_by_market_cap(mktcap_min=200e3, sectors=SectorConstants.FINANCE)
#     print(filtered_by_sector[:5])

#     # get tickers of 5 largest companies by market cap (specify sectors=SECTOR)
#     top_5 = get_biggest_n_tickers(5)
#     print(top_5)

