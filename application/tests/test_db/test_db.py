import pytest
from app import app
from application.models.database import db
from application.models.db_functions import filling_indexes_db,remove_indexes
# import application.models.database
from application.models.stocks import Indexes
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
from os import getenv


@pytest.fixture
def client():

    with app.test_client() as test_client:
        with app.app_context():
            yield test_client

@pytest.fixture(scope="session")
def engine():
    return create_engine(getenv("SQLALCHEMY_DATABASE_URI"))

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
        for etf in indexes_eft_list:
            assert Indexes.query.filter_by(ticker='SPLG').one_or_none() is not None


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
    count, data_historical = filling_indexes_db(current_data)
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
    count, data_historical = filling_indexes_db(current_data)
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

def test_removing(client,engine):
    Session = sessionmaker(engine)
    to_delete = 'QQQM'
    to_delete_1 = 'AAPL'
    remove_indexes(to_delete,to_delete_1)
    with Session() as session:
        test_stock = session.query(Indexes).filter(Indexes.ticker == to_delete).one_or_none()
        test_stock_1 = session.query(Indexes).filter(Indexes.ticker == to_delete_1).one_or_none()
    assert test_stock is None
    assert test_stock_1 is None

