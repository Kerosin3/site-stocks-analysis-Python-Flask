#https://addisonlynch.github.io/
#iexcloud.io
# https://addisonlynch.github.io/iexfinance/stable/usage.html?highlight=indexes
from iexfinance.stocks import Stock,get_historical_data
from datetime import date
from datetime import datetime, timedelta
import os
from iexfinance.utils.exceptions import  IEXQueryError
from .errors import ServerExeption,NoSuchStock,SomethingBadHappened
from bokeh.plotting import figure, output_file, show
from math import pi
import pandas as pd


os.environ["IEX_TOKEN"] = "Tpk_35acd01b094b4239aa87879709679d22"
os.environ["IEX_API_VERSION"] = "iexcloud-sandbox"

today = date.today()
end = today
start = datetime(2018, 1, 1)



def check_if_exists(func):
    def wrapper(*args,**kwargs):
        price = 0
        ticker = args[0]
        try:
            index_obj = Stock(ticker)
            # print('all is ok!')
            # print(index_obj)
            output = func(index_obj)
        except IEXQueryError:
            print('return nothing')
            return None
            # raise NoSuchStock
        except ValueError:
            raise NoSuchStock
        except:
            raise SomethingBadHappened('I dont know')
        else:
            return output

    return wrapper


def get_data_historical(ticker:str):
    '''
    parsing volumes and prices
    :param ticker:
    :return:
    '''
    assert (len(ticker) <= 4 ) and (len(ticker) > 0 )
    try:
        df = get_historical_data(ticker, start, end,
                                 output_format='pandas')
    except IEXQueryError:
        raise NoSuchStock
    # else:
    #     raise SomethingBadHappened

    dff = df.loc[:,['close',"volume"]]
    data_stocks = dff.to_dict()
    prices,volume = data_stocks['close'],data_stocks['volume']
    return prices,volume


def get_lastday_data(ticker:str):
    yesterday = date.today() + timedelta(days=-2)
    end = yesterday
    start = yesterday
    df = get_historical_data(ticker, start, end,
                             output_format='pandas')
    dff = df.loc[:,['close',"volume"]]
    data_stocks = dff.to_dict()
    prices,volume = data_stocks['close'].values(),\
                    data_stocks['volume'].values()
    return *prices,*volume


@check_if_exists
def get_today_price(index:Stock):
    price = index.get_price().to_dict()
    ticker = list(price.keys())[0]
    price = price[ticker]
    price = price['price']
    return price


def get_today_prices_several(indexex:list):
    stocks = Stock(indexex)
    prices = stocks.get_price().to_dict()
    out = {}
    for stock,price in prices.items():
        out[stock] = price['price']
    return out


def get_historical_for_graph(ticker:str):
    yesterday = date.today() + timedelta(days=-2)
    end = yesterday
    start = datetime(2019, 1, 1)
    df = get_historical_data(ticker, start, end,
                             output_format='pandas')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'date'}, inplace=True)
    df = df.loc[:, ['date', 'open', 'close', "volume", 'high', 'low']]
    df["date"] = pd.to_datetime(df["date"])
    inc = df.close > df.open
    dec = df.open > df.close
    w = 12 * 60 * 60 * 1000  # half day in ms
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title="MSFT Candlestick")
    p.xaxis.major_label_orientation = pi / 4
    p.grid.grid_line_alpha = 0.3
    p.segment(df.date, df.high, df.date, df.low, color="black")
    p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="#D5E1DD", line_color="black")
    p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")
    output_file("candlestick.html", title="candlestick.py example")
    return p
    # show(p)  # open a browse


