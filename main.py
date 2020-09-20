import sys
import os
import numpy as np
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

import streamlit as st
from datetime import date

# ------ owm modules ------
from import_trxn import *

pd.set_option('display.max_rows', 1000)
pd.options.display.float_format = '{:,.2f}'.format

st.header('US Stock Ticker')
# ----------------------------------------	
# -------- Transaction Filtering ---------
# ----------------------------------------

def get_stock_quote(stock_code):
	ticker = yf.Ticker(stock_code)
	df_ticker_info = pd.DataFrame.from_dict(ticker.info, orient='index', columns=['values']).reset_index()
	stock_quote = df_ticker_info[df_ticker_info['index'] == 'regularMarketPrice'].values[0,1]
	return stock_quote

def color_negative_red(val):
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color


df_trxn_raw = dataExtract()
df_trxn = df_trxn_raw

brokerOpt = st.sidebar.selectbox('Broker',('ALL', 'FUTU', 'IBKR', 'HSBC'))
if brokerOpt == 'ALL':
	df_trxn = df_trxn
elif brokerOpt == 'FUTU':
	df_trxn = df_trxn[df_trxn['Broker'] =='FUTU']
elif brokerOpt == 'IBKR':
	df_trxn = df_trxn[df_trxn['Broker'] == 'IBKR']
elif brokerOpt == 'HSBC':
	df_trxn = df_trxn[df_trxn['Broker'] == 'HSBC']

df_trxn = df_trxn.sort_values(by = ['TrxnDate','Symbol','Direction'])

# --------------------------------	
# -------- Summary Table ---------
# --------------------------------

df_summ_col = ['Symbol',
		'Avg Price',
		'OS Qty',
		'Total Cost',
		'Cur Price',
		'Acc Trade count',
		'Acc Trade amount',
		'Total Fee',
		'Rlz Rev',
		'UnRlz Rev']
		
df_summ = pd.DataFrame(columns=df_summ_col)

for index, row in df_trxn.iterrows():
	sym = row[1]
	dir = row[5]
	pri = row[6]
	qty = row[7]
	fee = row[8]

	# Buy new stock  
	if sym not in df_summ['Symbol'].unique() and dir == 'Buy':
		df_summ = df_summ.append({'Symbol' : sym,
								  'Avg Price' : pri,
								  'OS Qty': qty,
								  'Total Cost': pri*qty,
								  'Cur Price' : 0,
								  'Acc Trade count': 1,
								  'Acc Trade amount': pri*qty,
								  'Total Fee' : fee,
								  'Rlz Rev': 0,
								  'UnRlz Rev': 0
								 }, ignore_index = True)
							 
	# Buy existing stock  
	elif sym in df_summ['Symbol'].unique() and dir == 'Buy':
		i = df_summ[df_summ['Symbol'] == sym].index
		df_summ.loc[i, 'OS Qty'] = df_summ.loc[i, 'OS Qty'] + qty
		df_summ.loc[i, 'Total Cost'] = df_summ.loc[i, 'Total Cost'] + pri*qty
		df_summ.loc[i, 'Avg Price'] = df_summ.loc[i, 'Total Cost']  / df_summ.loc[i, 'OS Qty'] 
		df_summ.loc[i, 'Acc Trade count'] = df_summ.loc[i, 'Acc Trade count'] + 1
		df_summ.loc[i, 'Acc Trade amount'] = df_summ.loc[i, 'Acc Trade amount'] + pri*qty
		df_summ.loc[i, 'Total Fee'] = df_summ.loc[i, 'Total Fee'] + fee

	# Sell existing stock 
	elif sym in df_summ['Symbol'].unique() and dir == 'Sell':
		i = df_summ[df_summ['Symbol'] == sym].index
		df_summ.loc[i, 'OS Qty'] = df_summ.loc[i, 'OS Qty'] - qty
		df_summ.loc[i, 'Total Cost'] = df_summ.loc[i, 'Total Cost']  - df_summ.loc[i, 'Avg Price']  * qty
		df_summ.loc[i, 'Rlz Rev'] = df_summ.loc[i, 'Rlz Rev'] + (pri - df_summ.loc[i, 'Avg Price']) * qty
		if df_summ.loc[i[0], 'OS Qty']  <= 0: 
			df_summ.loc[i, 'Avg Price'] = 0
		else:
			df_summ.loc[i, 'Avg Price'] = df_summ.loc[i, 'Total Cost'] / df_summ.loc[i, 'OS Qty'] 
		df_summ.loc[i, 'Acc Trade count'] = df_summ.loc[i, 'Acc Trade count'] + 1
		df_summ.loc[i, 'Acc Trade amount'] = df_summ.loc[i, 'Acc Trade amount'] + pri*qty
		df_summ.loc[i, 'Total Fee'] = df_summ.loc[i, 'Total Fee'] + fee

try:
	df_summ['Cur Price'] = df_summ['Symbol'].apply(lambda x: get_stock_quote(x))
except:
	pass
	
df_summ['UnRlz Rev'] = (df_summ['Cur Price'] - df_summ['Avg Price']) * df_summ['OS Qty']
df_summ["Total PL"] = df_summ['Rlz Rev'] + df_summ['UnRlz Rev'] - df_summ['Total Fee']



# ------------------------
# ------- Dashboard ------
# ------------------------


# -------- Total PL -------
st.header('Total PL = US$ ' + '{:,.2f}'.format(df_summ["Total PL"].sum()))

# -------- Outstanding Portfolio breakdown -------
df_cur_port = df_summ[df_summ['OS Qty'] > 0]
df_cur_port['Cur Value'] = df_cur_port['OS Qty'] * df_cur_port['Cur Price']
fig = px.pie(df_cur_port, values='Cur Value', names='Symbol')
fig.update_traces(textposition='inside', textinfo='percent+label')
st.subheader('Portfolio Breakdown')
st.plotly_chart(fig)



# -------- Holding Table -------
if st.sidebar.checkbox("Show Holdings"):
	st.subheader('Holdings')
	portcurlist = ['Symbol','Cur Value','OS Qty','Cur Price','Avg Price','Rlz Rev','UnRlz Rev',"Total PL"]
	portlist_cursort = ['Cur Value','Symbol']
	st.table(df_cur_port[portcurlist].sort_values(by = portlist_cursort, ascending=False)
									.set_index('Symbol')
									.style.format({'Cur Value': "${:20,.0f}",
									'Cur Price': "${:,.2f}",
									'Avg Price': "${:,.2f}",
									'Rlz Rev': "${:+,.2f}",
									'UnRlz Rev': "${:+,.2f}",
									"Total PL": "${:+,.2f}"
									})
									.applymap(color_negative_red)
									)


# -------- Closed Table-------
if st.sidebar.checkbox("Show Closed"):
	st.subheader('Closed')
	df_cls_port = df_summ[df_summ['OS Qty'] == 0]
	df_cls_port['Cur Value'] = 0
	portclslist = ['Symbol',"Total PL"]
	portlist_clssort = ["Total PL",'Symbol']
	st.table(df_cls_port[portclslist].sort_values(by = portlist_clssort, ascending=False)
									.set_index('Symbol')
									.style.format({"Total PL": "${:+,.2f}"
									}))

# --------  Transaction Details-------
stockOpt = st.sidebar.multiselect('Select Stock',(df_trxn['Symbol'].sort_values().unique()))
if stockOpt:
	for s in stockOpt:
		df_hist = yf.download(s,date(2020,1,1),date.today()).reset_index()
		df_hist['Date'] = df_hist['Date'].dt.date
		df_hist['Symbol'] = s
		df_trxn_details = df_trxn[df_trxn['Symbol'].isin(stockOpt)]
		df_trxn_details = df_trxn_details.rename(columns={"TrxnDate": "Date"})
		df_hist_trxn = pd.merge(df_hist, df_trxn_details, on=['Symbol','Date'], how='left')
		
		df_hist_trxn.loc[df_hist_trxn['Direction'] == 'Buy', 'buySignal'] = df_hist_trxn['Adj Close']
		df_hist_trxn.loc[df_hist_trxn['Direction'] == 'Sell', 'sellSignal'] = df_hist_trxn['Adj Close']
		
		df_hist_trxn = df_hist_trxn[['Date','Adj Close','buySignal','sellSignal']]
		
		
		x = df_hist_trxn['Date']
		y_price = df_hist_trxn['Adj Close']
		y_buy = df_hist_trxn['buySignal']
		y_sell = df_hist_trxn['sellSignal']
		
		fig = go.Figure()
		fig.add_trace(go.Scatter(x=x, y=y_price,
						mode='lines',
						name='Price'))
		fig.add_trace(go.Scatter(x=x, y=y_buy,
						mode='markers',
						name='buy',
						marker_symbol='triangle-up',
						marker=dict(color='#03C04A', size=12)))
		fig.add_trace(go.Scatter(x=x, y=y_sell,
						mode='markers',
						name='Sell',
						marker_symbol='triangle-down',
						marker=dict(color='#D21404', size=12)))
		fig.update_layout(template='simple_white', title=s)
		st.plotly_chart(fig)
	
	if st.checkbox("Show Transaction Details", False):
		st.subheader('Transaction Details')
		st.table(df_trxn_details)
	

