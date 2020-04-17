import pandas as pd
import os.path
import numpy as np
import FinancialFunctions as FF


raw_data_path = os.path.abspath(os.getcwd()) + "\\"
ticker_file = "AAPL2000.csv"
prices = pd.read_csv(raw_data_path + ticker_file, index_col=0, parse_dates=True)

small_span = 12 
large_span = 26 
macd_span = 9

prices = FF.macd(prices, small_span, large_span, macd_span)

FF.plotMacd(prices)

positions=100
commission = 0.05
starting_capital = 10000
stoploss_percentage = 0.1

portfolio = FF.portfolio(prices, starting_capital, positions, commission, stoploss_percentage)