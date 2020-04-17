import pandas as pd
import os.path
import numpy as np
import FinancialFunctions as FF


raw_data_path = os.path.abspath(os.pardir)
raw_data_path = raw_data_path[:raw_data_path.rfind("code")] + "data\\raw\\"

ticker_file = "AAPL2000.csv"
prices = pd.read_csv(raw_data_path + ticker_file, index_col=0, parse_dates=True)

small_span = 12 
large_span = 26 
macd_span = 9

prices = FF.macd(prices, small_span, large_span, macd_span)

FF.plotMacd(prices)