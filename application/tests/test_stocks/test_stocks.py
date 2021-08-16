import pytest
from app import app
from application.models.database import db
from sqlalchemy import create_engine
from application.models.users import Users
from application.models.db_stocks import Stock_obj,Stock_data,Prices_tracking
from sqlalchemy.orm import Session,sessionmaker,load_only,session
from application.misc.stocks_functions import create_stock_obj
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

def test_add_stock(client,engine):
    user = db.session.query(Users).filter(Users.username == 'Alex').one_or_none()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
    # db.session.query(Prices_tracking).delete()
    # db.session.commit()
    Session = sessionmaker(engine)
    user0 = Users()
    user0.username = 'Alex'
    # print('=============',user0.username)
    db.session.add(user0)
    db.session.flush()
    db.session.refresh(user0)
    # print('id is ====',user0.id)
    p0 = Prices_tracking()
    p0.ticker = 'adbe'
    p0.user_related = user0.id
    p0.price_alert_less = 55.5
    db.session.add(p0)
    db.session.commit()
    ######
    p1 = Prices_tracking()
    p1.ticker = 'gggg'
    p1.user_related = user0.id
    p1.price_alert_less = 55.5
    db.session.add(p1)
    db.session.commit()
    # user = db.session.query(Users).filter(Users.username == 'Alex').one_or_none()
    # if user is not None:
    #     db.session.delete(user)
    #     db.session.commit()


    # with Session() as session:
    #     test_stock = session.query(Prices_tracking).\
    #         filter(Prices_tracking.user_related == user0.id).\
    #         all()
    #     for i in test_stock:
    #         print('======',i.ticker)

    with Session() as session:
        test_stock = session.query(Users).all()
        for i in test_stock:
            print('======', i.prices_alert.ticker)
    # p0 = Prices_tracking()
    # p0.ticker = 'adbe'
    # p0.user_related = user0.id
    # with Session() as session:
    #     # test_stock = session.query(Indexes).filter(Indexes.ticker == ticker).one_or_none()
    #     session.add(p0)
    #     session.commit()

def test_create_stock(client,engine):
    stock0 = Stock_obj()
    stock0.ticker = 'ADBE'
    user = db.session.query(Stock_obj).filter(Stock_obj.ticker == 'ADBE').one_or_none()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
    db.session.add(stock0)
    db.session.commit()
    db.session.flush()
    db.session.refresh(stock0)
    db.session.commit()

    sd = Stock_data()
    sd.today_price = 55.5
    # print('stock id is -------------',stock0.id)
    sd.Stock_obj_id = stock0.id
    # db.session.refresh(sd)
    # print('===============',sd.Stock_obj_id )
    db.session.add(sd)
    db.session.commit()

    # db.session.flush()
    # db.session.refresh(stock0)
    #
    # sd.stock_obj_ref = stock0.id
    #
    # user = db.session.query(Stock_obj).filter(Stock_obj.ticker == 'ADBE').one_or_none()
    # if user is not None:
    #     db.session.delete(user)
    #     db.session.commit()
    # with Session() as session:
    #     # test_stock = session.query(Indexes).filter(Indexes.ticker == ticker).one_or_none()
    #     session.add(p0)
    #     session.commit()

def test_create_stock_auto(client,engine):
    Session = sessionmaker(engine)
    ticker = 'NVDA'
    create_stock_obj(ticker)
    with Session() as session:
        test_stock = session.query(Stock_obj).filter(Stock_obj.ticker == ticker).one_or_none()
        assert test_stock.ticker == ticker

def test_id(client,engine):
    Session = sessionmaker(engine)
    ticker = 'NVDA'
    # db.session.query(Stock_obj).delete()
    # if (stock := db.session.query(Stock_obj).
    #         filter(Stock_obj.ticker == ticker).
    #         one_or_none()) == None:
    #     db.session.delete(stock)

    id = create_stock_obj(ticker)
    with Session() as session:
        test_stock = session.query(Stock_obj).filter(Stock_obj.ticker == ticker).one_or_none()
        assert test_stock.id == id

def test_relationship_stocks(client,engine):
    Session = sessionmaker(engine)
    ticker = 'NVDA'
    create_stock_obj(ticker)
    stock_id = db.session.query(Stock_obj).filter(Stock_obj.ticker == ticker).one()
    with Session() as session:
        test_data = session.query(Stock_data).filter(Stock_data.Stock_obj_id == stock_id.id).one_or_none()
        print(f'retrieved stock data is is {test_data.Stock_obj_id} and stock id is {stock_id.id} ')
        assert test_data is not None

def test_delete_stock_obj(client,engine):
    Session = sessionmaker(engine)
    ticker = 'NVDA'
    id = create_stock_obj(ticker)
    with Session() as session:
        stock = session.query(Stock_obj).\
            filter(Stock_obj.ticker == ticker).\
            one_or_none()
        if stock is not None:
            session.delete(stock)
            session.commit()
        else:
            raise
        assert db.session.query(Stock_obj).filter(Stock_obj.ticker == ticker).one_or_none() is None
        assert db.session.query(Stock_data).filter(Stock_data.Stock_obj_id == id).one_or_none() is None

def test_delete(client,engine):
    Session = sessionmaker(engine)
    ticker = 'NVDA'
    with Session() as session:
        test_data = session.query(Stock_obj).\
            filter(Stock_obj.ticker == ticker).one_or_none()
        session.delete(test_data)
        session.commit()
    assert db.session.query(Stock_obj).filter(Stock_obj.ticker == ticker).one_or_none() is None
