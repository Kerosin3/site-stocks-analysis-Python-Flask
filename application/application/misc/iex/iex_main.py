from iexfinance.refdata import get_symbols
import pandas as pd
import os
# from app import app

def get_all_symbols():
    path = os.path.join(app.root_path, "application",'misc','iex')
    print('==============',path)
    all_obj = get_symbols()[:]
    # print(path + 'all_symbols',type(all_obj))
    all_tickers = all_obj["symbol"]
    all_tickers.to_csv(path + '/all_symbols.csv', sep='\t', encoding='utf-8',index=False) # write
