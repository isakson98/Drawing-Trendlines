In my senior project, I am developing a unique infrastructure for stock analysis. I am very fond of technical analysis and chart patterns, and I want to see whether I can find a way to optimize finding the most profitable setups. 

In essense, after having retrieved high quality data from Polygon (current as well as delisted tickers), I want to assign a pattern on a chart for my program to look for. Having found the pattern, I will then collect different statistics about each individual setup and label each setup as successful or not. I will then use these statistics to train a neural network model. 

As my first setup, I decided to go with a breakout on an uptrending stock. I use linear regression to identify trendlines and breakouts from them. I label each breakout based on the sell rules that I specify. I collect details about these trendlines (duration, % from previous low, proportion of wicks, etc) and train and test a dense neural network model using this data.

This project is highly scalable. For my senior project, I am building the infrastructure itself and the end-to-end example of how this infrastructure can be utilized.