import time
from pandas import DataFrame
from datetime import date
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker,load_only
from .stocks import Indexes
from application.misc.stocks_getter import get_data_for_plotting,get_today_price
from application.models.stocks import create_index
from iexfinance.utils.exceptions import IEXQueryError
from flask import flash
from os import getenv
from sqlalchemy import create_engine



def filling_indexes_db(time0:datetime=datetime.now(),
                       list_new_indexes=None):
    engine = create_engine(getenv("SQLALCHEMY_DATABASE_URI"))
    Session = sessionmaker(engine)
    current_day_prices = {}
    last_day_prices = {}
    data_historical = {}
    today = time0
    count = 0
    if (list_new_indexes is not None ) and (list_new_indexes):
        with Session() as session:
            for index in list_new_indexes:
                #add if there is no such symbol in db
                if session.query(Indexes).filter(Indexes.ticker == index).one_or_none() is None:
                    try:
                        print('INDEX ticker ---------------------',index)
                        new_index, _ = create_index(index)
                    except IEXQueryError:
                        print('Error!!!!')
                        return 0
                    else:
                        session.add(new_index)
                        session.commit()
                        print('Added indexes:', index)
                    # finally:
                        # print('DONE===================================')
                    # count+=1
                else:
                    # flash('This stock has been already added')
                    return 1
    with Session() as session: #asking for dates
        data_collection = session.query(Indexes). \
            options(load_only(Indexes.changed_at))  # загружает всё..????
        for datez in data_collection:
            if datez.changed_at.date() < today.date(): #for a ticker
                print('updating',datez.ticker)
                data_new = get_data_for_plotting(datez.ticker)
                session.query(Indexes). \
                    filter(Indexes.id == datez.id). \
                    update(
                    {"index_value_today": get_today_price(datez.ticker),
                     "index_value_yesterday": data_new['close'].iloc[-1],
                     "history_data": data_new,
                     # change automatically!
                     })
                session.commit()
            else:
                pass  # do nothing, data for this index is already up to date
                # return data anyway . i.e already is up to date
        full_data = session.query(Indexes).all() #getting all data
        for index in full_data:
            count+=1
            # print(count)
            ticker = index.ticker
            last_day_prices[ticker] = index.index_value_yesterday
            current_day_prices[ticker] = index.index_value_today
            data_historical[ticker] = index.history_data
    return  current_day_prices,   last_day_prices, count, data_historical

def remove_indexes(*args):
    engine = create_engine(getenv("SQLALCHEMY_DATABASE_URI"))
    Session = sessionmaker(engine)
    if len(args) != 0:
        with Session() as session:
            for index in args:
                index_to_delete = session.query(Indexes).\
                    filter(Indexes.ticker == index).one_or_none()
                if index_to_delete is not None:
                    session.delete(index_to_delete)
                    session.commit()
                    print('removing',index)
                else: # thes isnt
                    return 0
        session.commit()
        return 1
    else:
        raise

