import sys
import numpy as np
import pandas as pd
import yfinance as yf

def get_stock_quote(stock_code):
	ticker = yf.Ticker(stock_code)
	df_ticker_info = pd.DataFrame.from_dict(ticker.info, orient='index', columns=['values']).reset_index()
	stock_quote = df_ticker_info[df_ticker_info['index'] == 'regularMarketPrice'].values[0,1]
	return stock_quote
