from iexfinance.refdata import get_symbols
import pytest
from app import app
import pandas as pd

def test_all_symbols():
    all_obj = get_symbols()[:]
    size = all_obj.shape[0]
    all_tickers =all_obj["symbol"]
    print(size)
    print(all_tickers)
    assert all_obj.equals(all_obj)

