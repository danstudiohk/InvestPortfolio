import os
import sqlite3
from sqlalchemy import create_engine
from import_trxn import *

# df_trxn_raw = dataExtract()
# df_trxn_raw.reset_index()

# print(df_trxn_raw.head(10))

engine = create_engine('sqlite:///trxn.db', echo=False)
# df_trxn_raw.to_sql('trxn', con=engine, if_exists='replace', index =True)


df = pd.read_sql('select * from trxn', con=engine, index_col = 'index')
print(df.dtypes)