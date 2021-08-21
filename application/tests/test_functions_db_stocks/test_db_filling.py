import config
import pytest
from app import app
from application.models.database import db
from sqlalchemy import create_engine
from application.models.users import Users
from application.models.db_stocks import Stock_obj,Stock_data,Prices_tracking
from sqlalchemy.orm import Session,sessionmaker,load_only,session
from application.misc.stocks_functions import create_stock_obj
from .conftest import myfixture
from application.misc.stocks_functions import get_hist_data
from application.misc.stocks_functions import create_stock_obj


engine = create_engine(config.TestingConfig.SQLALCHEMY_DATABASE_URI)
import pandas as pd
Session = sessionmaker(engine)


@pytest.fixture
def client():
    # engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')
    # Session = sessionmaker(engine)
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client

@pytest.fixture(scope="session")
def engine():
    return create_engine(config.TestingConfig.SQLALCHEMY_DATABASE_URI)

@pytest.fixture
def test_data_fixture(myfixture):
    ticker = myfixture
    id_fix = None
    with Session() as session:
        full_data = session.query(Stock_obj).all()
        for obj in full_data:
            session.delete(obj)
            session.commit()
    id_fix = create_stock_obj(ticker)
    print('created stock obj with id',id_fix)
    yield id_fix
    with Session() as session:
        test_data = session.query(Stock_obj). \
            filter(Stock_obj.ticker == ticker).one_or_none()
        if test_data is not None:
            session.delete(test_data)
            session.commit()

def test_data_getter(client,myfixture,test_data_fixture):
    with Session() as session:
        test_data = session.query(Stock_obj). \
            filter(Stock_obj.id == test_data_fixture).one_or_none()
        assert test_data is not None

def test_creation_and_filling_values(client,myfixture,test_data_fixture):
    with Session() as session:
        # test_stock = session.query(Stock_obj). \
        #     filter(Stock_obj.id == test_data_fixture).one_or_none()
        # assert test_stock is not None
        test_stock_data = session.query(Stock_data). \
            join(Stock_obj). \
            filter(Stock_data.Stock_obj_id == test_data_fixture). \
            one_or_none()
        df = test_stock_data
        print('============',df.historical_data)
        print('today price',df.today_price)
        print('today price',test_stock_data.changed_at)
        assert df.historical_data.empty is False
