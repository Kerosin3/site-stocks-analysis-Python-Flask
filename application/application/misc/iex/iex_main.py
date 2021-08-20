from iexfinance.refdata import get_symbols
import pandas as pd
import os

def get_all_symbols():
    cwd = os.getcwd()
    path = os.path.join(cwd, "application",'misc','iex')
    print('==============',path)
    all_obj = get_symbols()[:]
    # print(path + 'all_symbols',type(all_obj))
    all_tickers = all_obj["symbol"]
    all_tickers.to_csv(path + '/all_symbols.csv', sep='\t', encoding='utf-8',index=False) # write
