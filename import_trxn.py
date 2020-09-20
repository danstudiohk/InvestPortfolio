import os
import sys
import numpy as np
import pandas as pd

# -------- READ Transaction Data ----------
def dataExtract():
	TradeTrxn_path = r'C:\Users\Daniel\Documents\GitHub\InvestPortfolio\TradeTrxn.xlsx'
	trxn_futu = pd.read_excel(TradeTrxn_path, sheet_name='FUTU',index_col=0).reset_index()
	trxn_ibkr = pd.read_excel(TradeTrxn_path, sheet_name='IBKR',index_col=0).reset_index()
	trxn_hsbc = pd.read_excel(TradeTrxn_path, sheet_name='HSBC',index_col=0).reset_index()

	varlist = ['Broker'
				,'Symbol'
				,'TrxnDate'
				,'TrxnYear'
				,'TrxnMonth'
				,'Direction'
				,'Price'
				,'Quantity'
				,'Fee']

	# -------- FUTU ----------
	trxn_futu['Broker'] = 'FUTU'
	trxn_futu['TrxnDate'] = trxn_futu['Filled Time'].dt.date
	trxn_futu['TrxnYear'] = trxn_futu['Filled Time'].dt.year
	trxn_futu['TrxnMonth'] = trxn_futu['Filled Time'].dt.month
	trxn_futu['Fee'] = trxn_futu['Quantity']*0.003 + 0.99 + 1

	df_trxn_futu = trxn_futu[varlist]

	# -------- IBKR ----------
	trxn_ibkr['Broker'] = 'IBKR'
	trxn_ibkr['TrxnDateTime'] = trxn_ibkr['Date/Time'].str[:10].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
	trxn_ibkr['TrxnDate'] = trxn_ibkr['TrxnDateTime'].dt.date
	trxn_ibkr['TrxnYear'] = trxn_ibkr['TrxnDateTime'].dt.year
	trxn_ibkr['TrxnMonth'] = trxn_ibkr['TrxnDateTime'].dt.month
	trxn_ibkr['Quantity'] = abs(trxn_ibkr['Quantity'])
	trxn_ibkr['Price'] = abs(trxn_ibkr['T. Price'])
	trxn_ibkr['Direction'] = np.where(trxn_ibkr['Code']=='O', 'Buy', 'Sell')
	trxn_ibkr['Fee'] = abs(trxn_ibkr['Comm/Fee'])

	df_trxn_ibkr= trxn_ibkr[varlist]

	# -------- HSBC ----------
	trxn_hsbc['Broker'] = 'HSBC'
	trxn_hsbc['TrxnDate'] = trxn_hsbc['TrxnDateTime'].dt.date
	trxn_hsbc['TrxnYear'] = trxn_hsbc['TrxnDateTime'].dt.year
	trxn_hsbc['TrxnMonth'] = trxn_hsbc['TrxnDateTime'].dt.month
	trxn_hsbc['Fee'] = 18

	df_trxn_hsbc= trxn_hsbc[varlist]

	# -------- Append ----------
	df_trxn_raw = df_trxn_futu.append(df_trxn_ibkr).append(df_trxn_hsbc).reset_index(drop=True)
	return df_trxn_raw


