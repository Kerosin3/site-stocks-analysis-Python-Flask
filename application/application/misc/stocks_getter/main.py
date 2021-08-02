#https://addisonlynch.github.io/
#iexcloud.io
from iexfinance.stocks import Stock,get_historical_data
from datetime import date
from datetime import datetime, timedelta
os.environ["IEX_TOKEN"] = "Tpk_35acd01b094b4239aa87879709679d22"
os.environ["IEX_API_VERSION"] = "iexcloud-sandbox"

today = date.today()
end = today
start = datetime(2018, 1, 1)



def get_data_historical(ticker:str):
    '''
    parsing volumes and prices
    :param ticker:
    :return:
    '''
    assert len(ticker) == 4
    df = get_historical_data(ticker, start, end,
                             output_format='pandas')
    dff = df.loc[:,['close',"volume"]]
    data_stocks = dff.to_dict()
    prices,volume = data_stocks['close'],data_stocks['volume']
    return prices,volume

def get_lastday_data(ticker:str):
    yesterday = date.today() + timedelta(days=-1)
    end = yesterday
    start = yesterday
    df = get_historical_data(ticker, start, end,
                             output_format='pandas')
    dff = df.loc[:,['close',"volume"]]
    data_stocks = dff.to_dict()
    prices,volume = data_stocks['close'],data_stocks['volume']
    return prices,volume
