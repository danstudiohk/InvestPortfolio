import pandas as pd
import yfinance as yf
import streamlit as st

lst = ['AMZN', 'AAPL','SQQQ']
hist = yf.download(lst, start="2018-01-01", end="2020-12-31")


df = pd.DataFrame()
for i in lst:
	info = yf.Ticker(i)
	info_df_org = pd.DataFrame.from_dict(info.info, orient='index').T
	df = df.append(info_df_org)
print(df)
print(df.columns)


col = ['symbol','shortName','regularMarketPrice','regularMarketDayHigh','regularMarketDayRange',
'regularMarketDayLow','regularMarketVolume','regularMarketPreviousClose',
'fullExchangeName','regularMarketOpen','regularMarketChange','regularMarketChangePercent','marketCap']

