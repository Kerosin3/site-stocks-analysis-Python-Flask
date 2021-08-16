import pytest
from app import app
from application.models.database import db
from sqlalchemy import create_engine
from application.models.users import Users
from application.models.db_stocks import Stock_obj,Stock_data,Prices_tracking
from sqlalchemy.orm import Session,sessionmaker,load_only,session
from application.misc.stocks_functions import create_stock_obj
from .conftest import username_fixture
from application.models.users import Users
from application.misc.user_db_funct import create_user
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

@pytest.fixture
def test_data_fixture(username_fixture):
    username = username_fixture
    with Session() as session:
        userlist = session.query(Users).all()
        for obj in userlist:
            session.delete(obj)
            session.commit()
            print('Clearing user list')
    id_fix = create_user(username)
    user_to_delete = session.query(Users). \
        filter(Users.username == username_fixture).one_or_none()
    print(f'created stock obj with id {id_fix}, and username {user_to_delete.username}')
    yield id_fix
    with Session() as session:
        user_to_delete = session.query(Users). \
            filter(Users.username == username_fixture).one_or_none()
        if user_to_delete is not None:
            session.delete(user_to_delete)
            session.commit()


def test_user_creation(client,username_fixture,test_data_fixture):
    with Session() as session:
        user_to_create = session.query(Users). \
            filter(Users.username == username_fixture).one_or_none()
        assert user_to_create is not None
        print(user_to_create)
