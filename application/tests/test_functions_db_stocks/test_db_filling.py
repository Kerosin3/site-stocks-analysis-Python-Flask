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
engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')

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
    return create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')


def test_data_getter():
    ticker = 'TSLA'
    out = get_hist_data(ticker)
    print(out)
    assert out is not None

def test_creation_and_filling():
    pass
