
'''

This class will develop statistics about each individual trendline.

Statistics developed will be features for the neural network 

'''

class TrendlineProcessing:
    
    '''
    params:
        trendlines_df -> dataframe straight from self.identify_trendlines_LinReg()

    remove trendlines where the end price of the trendline is higher than origin.
    
    Decided to have this function outside of the main trendline drawing function 
    to avoid clustering too many things in it.

    returns:
        descending_df -> same columns 
    '''
    def remove_ascending_trendlines(self, trendlines_df):

        if "price_start" not in trendlines_df.columns:
            print('''Cannot remove trendlines. There is no "price_start" column in trendlines_df''')
            return trendlines_df
        
        return trendlines_df[(trendlines_df["price_start"] > trendlines_df["price_end"] )]

    
    '''
    params:
        trendlines_df -> dataframe straight from self.identify_trendlines_LinReg()

    remove trendlines where the end price of the trendline is higher than origin

    returns:
        ascending_df -> same columns 
    '''
    def remove_descending_trendlines(self, trendlines_df):

        if "price_start" not in trendlines_df.columns:
            print('''Cannot remove trendlines. There is no "price_start" column in trendlines_df''')
            return trendlines_df

        return trendlines_df[(trendlines_df["price_start"] < trendlines_df["price_end"] )]
         
    '''
    
    Along the process of drawing the trendlines, there will be cases where certain trendlines will be
    drawn more than once, and I defintely do not want to include them in the dataset.
    
    '''
    def remove_duplicate_trendlines(self, trendlines_df):

        return trendlines_df[~trendlines_df.duplicated()]

