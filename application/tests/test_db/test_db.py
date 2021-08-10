import pytest
from app import app
from application.models.database import db
from application.models.db_functions import filling_indexes_db,engine
# import application.models.database
from application.models.stocks import Stock_one,Stock_data,Indexes
import random
from application.models import create_index
import time
from pandas import DataFrame
from datetime import date
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker,load_only,session
from application.misc.stocks_getter import get_today_price,get_data_for_plotting
# from application.models.database import filling_indexes_db

# engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')
# Session = sessionmaker(engine)

@pytest.fixture
def client():
    # engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')
    # Session = sessionmaker(engine)
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client

@pytest.fixture(scope="session")
def engine():
    return create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')

# def add_test_index(ticker:str):
#     out = Indexes()
#     Indexes.ticker = ticker
#     Indexes.index_value = random.randint(0,99)
#     return out


@pytest.fixture
def test_data():
    db.session.query(Indexes).delete()
    db.session.commit()
    out = None
    ticker = 'TSLA'
    test_stock = Indexes.query.filter_by(ticker=ticker).one_or_none()
    if test_stock is not None:
        Indexes.query.filter_by(ticker=ticker).delete()
    else:
        out = Indexes()
        out.ticker = ticker
        out.index_value = random.randint(0, 99)
        db.session.add(out)
        db.session.commit()
    yield 0
    Indexes.query.filter_by(ticker=ticker).delete() # teardown
    db.session.commit()




def test_add_stock(client,test_data):
    ticker = 'TSLA'
    assert Indexes.query.filter_by(ticker=ticker).count() == 1
    assert Indexes.query.filter_by(ticker=ticker).one_or_none() is not None

def test_index_creation(client):
    db.session.query(Indexes).delete()
    db.session.commit()
    an_index = 'SPLG'
    out,data = create_index(an_index)
    db.session.add(out)
    db.session.commit()
    index = Indexes.query.filter_by(ticker=an_index).one_or_none()
    # assert index.history_data == data
    assert data.equals(index.history_data) #check the data
    assert index is not None
    # assert index.created_at <= index.changed_at
    # print(data)
    # print('===================',type(out.history_data))
    # print('===================',(out.index_value_yesterday))
    # print('===================',(out.changed_at))


def test_index_change(client):
    db.session.query(Indexes).delete()
    db.session.commit()
    an_index = 'SPLG'
    out,_ = create_index(an_index) # filling values
    db.session.add(out)
    db.session.commit()
    data_creating = Indexes.query.filter_by(ticker=an_index).one().created_at #created
    db.session.commit()
    time.sleep(3)
    index = Indexes.query.filter_by(ticker=an_index).one_or_none()
    index.index_value_today = 666 #change value
    data_changed = Indexes.query.filter_by(ticker=an_index).one().changed_at #changed
    db.session.commit()
    print('------------------------',data_creating)
    print('===================', data_changed)
    assert data_changed > data_creating

def test_filling_base(client,engine):
    Session = sessionmaker(engine)
    db.session.query(Indexes).delete()
    db.session.commit()
    indexes_eft_list = [
        'SPLG',
        'QQQM',
        'DIA',
        'IWM'
    ]
    current_day_prices = {}
    last_day_prices = {}
    with Session() as session:
        for index in indexes_eft_list:
            new_index,_ = create_index(index)
            session.add(new_index)
            session.commit()
    with Session() as session:
        xxx = Indexes.query.filter_by(ticker='SPLG').one()
        # print(xxx.history_data.loc[[-1,-1],['close',"volume"]])
        print(xxx.index_value_yesterday)
        print(xxx.index_value_today)
        # print(xxx.history_data.iloc[-1])

# def test_whether_update(client):
#     db.session.query(Indexes).delete()
#     db.session.commit()
#     indexes_eft_list = [
#         'SPLG',
#         'QQQM',
#         'DIA',
#         'IWM'
#     ]
#     current_day_prices = {}
#     last_day_prices = {}
#     for index in indexes_eft_list:
#         index, _ = create_index(index)
#         db.session.add(index)
#     db.session.commit()
#     # filled db
#     # today = date.today()
#     data_changed = Indexes.query.filter_by(ticker='SPLG').one().changed_at  # changed
#     if data_changed.date() == datetime.today().date(): #just returning value
#         print('WE ARE HERE======================')
#         for index in indexes_eft_list:
#             current_day_prices[index] = Indexes.query.filter_by\
#                 (ticker=index).one().index_value_today
#             last_day_prices[index] = Indexes.query.filter_by\
#                 (ticker=index).one().index_value_yesterday
#         db.session.commit()
#     elif data_changed.date() < datetime.today().date(): #filling if there is some data to update
#         for index in indexes_eft_list:
#             index, _ = create_index(index)
#             db.session.add(index)
#         db.session.commit()
#     else:
#         raise # is impossible
#     today = date.today()
#     # date0 = datetime(2021, 8, 9, 12, 55, 16)
#     assert  bool(current_day_prices) == True #there something
#     assert  bool(last_day_prices) == True  #there something


def test_db_filling_update_not_need(client,engine):
    Session = sessionmaker(engine)
    current_data = datetime.now() + timedelta(days=-2) # data in db is ahead
    # print('current data',current_data)
    current_day_prices,   last_day_prices = {}, {}
    count, data_historical = 0, {}
    change_data = {}
    #getting change date
    with Session() as session:
        full_data = session.query(Indexes).all()
        for indexes in full_data:
            change_data[indexes.ticker] = indexes.changed_at
    #getting data and change it if need !!!
    current_day_prices,   last_day_prices,  \
    count, data_historical = filling_indexes_db(current_data,Session)
    with Session() as session:
        full_data = session.query(Indexes).all()
        for indexes in full_data:
            assert indexes.changed_at == change_data[indexes.ticker]

def test_db_filling_update_needs(client,engine):
    Session = sessionmaker(engine)
    current_data = datetime.now() + timedelta(days=2) # data in db are old
    # print('current data',current_data)
    current_day_prices,   last_day_prices = {}, {}
    count, data_historical = 0, {}
    change_data = {}
    #getting change date
    with Session() as session:
        full_data = session.query(Indexes).all()
        for indexes in full_data:
            change_data[indexes.ticker] = indexes.changed_at
    #getting data and change it if need !!!
    current_day_prices,   last_day_prices,  \
    count, data_historical = filling_indexes_db(current_data,Session)
    with Session() as session:
        full_data = session.query(Indexes).all()
        for indexes in full_data:
            assert indexes.changed_at > change_data[indexes.ticker]

#just one and update
def test_add_new_indexes(client,engine):
    Session = sessionmaker(engine)
    ticker = 'TSLA'
    # count0 = Indexes.query.all().count
    with Session() as session:
        test_stock = session.query(Indexes).filter(Indexes.ticker == ticker).one_or_none()
        if test_stock is not None:
            session.delete(test_stock)
            session.commit()
        count0 = session.query(Indexes).count()
    # if test_stock is not None:
    #     Indexes.query.filter_by(ticker=ticker).delete()
    #     db.session.commit()
    current_data = datetime.now() + timedelta(days=2)  # data in db are old
    list0 = ['TSLA']
    _,_,count_items,_ = filling_indexes_db(current_data,list_new_indexes=list0)
    with Session() as session:
        count1 = session.query(Indexes).count()
    print(count_items)
    assert count0 + 1 == count1

def test_add_new_empty_indexes(client,engine):
    Session = sessionmaker(engine)
    # count0 = Indexes.query.all().count
    ticker = 'TSLA'
    with Session() as session:
        test_stock = session.query(Indexes).filter(Indexes.ticker == ticker).one_or_none()
        if test_stock is not None:
            session.delete(test_stock)
            session.commit()
        count0 = session.query(Indexes).count()
    # if test_stock is not None:
    #     Indexes.query.filter_by(ticker=ticker).delete()
    #     db.session.commit()
    current_data = datetime.now() + timedelta(days=2)  # data in db are old
    list0 = []
    print(bool(list0))
    _,_,count_items,_ = filling_indexes_db(current_data,list_new_indexes=list0)
    with Session() as session:
        count1 = session.query(Indexes).count()
    print(count_items)
    assert count0  == count1


# def test_session(client,engine):
#     Session = sessionmaker(engine)
#     dates = []
#     max_date = None
#     today = date.today()
#     today = datetime.now() + timedelta(days=-1)
#     current_day_prices = {}
#     last_day_prices = {}
#     data_historical = {}
#     # engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')
#     with Session() as session:
#         data_collection = session.query(Indexes).\
#             options(load_only(Indexes.changed_at)) # загружает всё..????
#         for datez in data_collection:
#             if datez.changed_at < today: #if new data is available for an index
#                 data_new = get_data_for_plotting(datez.ticker)
#                 session.query(Indexes). \
#                     filter(Indexes.id == datez.id). \
#                     update(
#                     {"index_value_today": get_today_price(datez.ticker),
#                     "index_value_yesterday": data_new['close'].iloc[-1],
#                     "history_data": data_new,
#                     # change automatically!
#                      })
#                 session.commit()
#             else:
#                 pass #do nothing, data for this index is already up to date
#         # return data anyway . i.e already is up to date
#         full_data = session.query(Indexes).all()
#         for index in full_data:
#             ticker = index.ticker
#             last_day_prices[ticker] = index.index_value_yesterday
#             current_day_prices[ticker] = index.index_value_today
#             data_historical[ticker] = index.history_data
#     for i,j in last_day_prices.items():
#         print(i,j)
#     assert bool(last_day_prices) == True

