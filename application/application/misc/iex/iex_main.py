from iexfinance.refdata import get_symbols
#all_symbols =

def get_all_symbols():
    all_obj = get_symbols()[:]
    if not all_obj.equals(all_obj):
        all_tickers = all_obj["symbol"]
        return all_tickers
    else:
        return None

