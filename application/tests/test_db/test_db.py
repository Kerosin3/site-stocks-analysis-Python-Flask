import pytest
from app import app
from application.models.database import db
from application.models.stocks import Stock_one,Stock_data,Indexes
import random
from application.models import create_index
import time
from pandas import DataFrame
from datetime import date
from datetime import datetime, timedelta
@pytest.fixture
def client():
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client

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

def test_filling_base(client):
    db.session.query(Indexes).delete()
    db.session.commit()
    # def wrapper_commiting(func):
    #     def top(args):
    #         out,_ = func()
    #         db.session.add(out)
    #         db.session.commit()
    #     return wrapper
    #
    # create_index()
    indexes_eft_list = [
        'SPLG',
        'QQQM',
        'DIA',
        'IWM'
    ]
    current_day_prices = {}
    last_day_prices = {}
    for index in indexes_eft_list:
        index,_ = create_index(index)
        db.session.add(index)
    db.session.commit()
    for index in indexes_eft_list:
        assert  Indexes.query.filter_by(ticker=index).\
                    one_or_none() is not None

def test_whether_update(client):
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
    for index in indexes_eft_list:
        index, _ = create_index(index)
        db.session.add(index)
    db.session.commit()
    # filled db
    # today = date.today()
    data_changed = Indexes.query.filter_by(ticker='SPLG').one().changed_at  # changed
    if data_changed.date() == datetime.today().date(): #just returning value
        print('WE ARE HERE======================')
        for index in indexes_eft_list:
            current_day_prices[index] = Indexes.query.filter_by\
                (ticker=index).one().index_value_today
            last_day_prices[index] = Indexes.query.filter_by\
                (ticker=index).one().index_value_yesterday
        db.session.commit()
    elif data_changed.date() < datetime.today().date(): #filling
        for index in indexes_eft_list:
            index, _ = create_index(index)
            db.session.add(index)
        db.session.commit()
    else:
        raise # is impossible
    today = date.today()
    # date0 = datetime(2021, 8, 9, 12, 55, 16)
    assert  bool(current_day_prices) == True
    assert  bool(last_day_prices) == True


