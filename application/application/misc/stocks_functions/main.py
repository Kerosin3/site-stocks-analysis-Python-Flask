from application.models.db_stocks import Stock_obj,Stock_data,Prices_tracking
from application.models.database import db
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker,load_only
from iexfinance.stocks import Stock,get_historical_data
from datetime import date
from datetime import datetime, timedelta
import os
from iexfinance.utils.exceptions import  IEXQueryError
from iexfinance.stocks import Stock,get_historical_data


engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')
os.environ["IEX_TOKEN"] = "Tpk_35acd01b094b4239aa87879709679d22"
os.environ["IEX_API_VERSION"] = "iexcloud-sandbox"


def get_hist_data(ticker:str):
    yesterday = date.today() + timedelta(days=-1)
    end = date.today()
    start = datetime(2019, 1, 1)
    try:
        df = get_historical_data(ticker, start, end,
                             output_format='pandas') # from yestrday
    except IEXQueryError:
        print('Error!!!!')
        return None
    else:
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'date'}, inplace=True)
        df = df.loc[:, ['date', 'open', 'close', "volume", 'high', 'low']]
        return df

def get_today_price(ticker:str):
    try:
        stock = Stock(ticker)
    except IEXQueryError:
        return None
    else:
        price = stock.get_price().to_dict()
        price = price[ticker]
        price = price['price']
        return price

def create_stock_obj(ticker:str,
                     Session=sessionmaker(engine)):
    today = datetime.now()
    with Session() as session:
        checker = session.query(Stock_obj). \
            filter(Stock_obj.ticker == ticker).one_or_none()
        if checker is not None: # exists lets update
            id = checker.id
            test_stock_data = session.query(Stock_data). \
                join(Stock_obj). \
                filter(Stock_data.Stock_obj_id == id). \
                one()
            last_change = test_stock_data.changed_at
            if last_change.date() < today.date(): #echecking whether update required
                test_stock_data.historical_data = get_hist_data(ticker)
                print(f'updating {ticker} data')
                session.flush()
                session.refresh(test_stock_data)
                return test_stock_data.id
            else:
                pass # no need to update
        else:
            pass # pass i.e stock is not exists
    #creating stock
    with Session() as session:
        out = Stock_obj()
        out.ticker = ticker
        data = Stock_data()
        hist_data_0 = get_hist_data(ticker)
        if hist_data_0 is None: #already exists
            raise
        data.historical_data = hist_data_0 #fill historical data
        price_today = get_today_price(ticker)
        if price_today is None:
            raise
        data.today_price = price_today #fillig today price
        session.add(out)
        session.flush()
        session.refresh(out)
        id = out.id
        # session.commit()
        data.Stock_obj_id = out.id
        session.add(data)
        session.commit()
        print('creating................',id)
    return id

def create_track_price_object(ticker:str,id:int,Session=sessionmaker(engine)):
    with Session() as session:
        check = session.query(Prices_tracking). \
            filter(Prices_tracking.ticker == ticker).one_or_none()
        #already exists
        if check is not None:
            return None
        else:
            p0 = Prices_tracking()
            p0.ticker = ticker
            p0.user_related = id
            session.add(p0)
            session.flush()
            session.refresh(p0)
            id_out = p0.user_related
            session.commit()
            return id_out

# def get_hist_data(ticker:str):
#     pass

