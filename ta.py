import pandas as pd
from datetime import date
import streamlit as st
import yfinance as yf
import talib
import plotly.graph_objects as go

def dl_hist(ticker,startDate,endDate):
	df_hist = yf.download(ticker, startDate, endDate, period = '1d').reset_index()
	return df_hist
	
def calc_sig():
	df_hist = dl_hist(ticker, startDate, endDate)
	df_hist['20MA'] = talib.SMA(df_hist['Close'], timeperiod=20)
	df_hist['50MA'] = talib.SMA(df_hist['Close'], timeperiod=50)
	df_hist['120MA'] = talib.SMA(df_hist['Close'], timeperiod=120)
	df_hist['RSI'] = talib.RSI(df_hist['Close'], timeperiod=14)
	df_hist['SAR'] = talib.SAR(df_hist['High'], df_hist['Low'], acceleration=0, maximum=0)
	df_hist['20MA_lag1'] = df_hist['20MA'].shift(1)
	df_hist['50MA_lag1'] = df_hist['50MA'].shift(1)

	df_hist.loc[(df_hist['20MA'] > df_hist['50MA']) & (df_hist['20MA_lag1'] < df_hist['50MA_lag1']) , 'SignalBuy'] = df_hist['20MA']

	return df_hist

def hist_plot():
	x = df_hist['Date']
	y_price = df_hist['Close']
	y_20MA = df_hist['20MA']
	y_50MA = df_hist['50MA']
	y_buy = df_hist['SignalBuy']
	
	fig = go.Figure()
	fig.add_trace(go.Candlestick(x=x, 
					open=df_hist['Open'],
					high=df_hist['High'],
					low=df_hist['Low'],
					close=df_hist['Close']))
	# fig.add_trace(go.Scatter(x=x, y=y_20MA,
					# mode='lines',
					# name='y_20MA'))
	# fig.add_trace(go.Scatter(x=x, y=y_50MA,
					# mode='lines',
					# name='y_50MA'))
	fig.add_trace(go.Scatter(x=x, y=y_buy,
					mode='markers',
					name='buy',
					marker_symbol='triangle-up',
					marker=dict(color='#03C04A', size=12)))
	fig.update_layout(template='simple_white')
	st.plotly_chart(fig)
	

ticker = st.sidebar.text_input("ticker")
startDate = st.sidebar.date_input("Period Start", date(2018, 1, 1))
endDate = st.sidebar.date_input("Period End", date.today())

buySig = st.sidebar.selectbox('Select Buying Signal',['A','B','C'])
sellSig = st.sidebar.selectbox('Select Selling Signal',['A','B','C'])

if st.sidebar.button('Run'):
# execute the task
	df_hist = calc_sig()
	hist_plot()