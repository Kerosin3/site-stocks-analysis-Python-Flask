import pytest
from app import app
from application.models.database import db
from sqlalchemy import create_engine
from application.models.users import Users
from application.models.db_stocks import Stock_obj, Stock_data, Prices_tracking
from sqlalchemy.orm import Session, sessionmaker, load_only, session
from application.misc.stocks_functions import create_stock_obj
from .conftest import username_fixture
from application.models.users import Users
from application.misc.user_db_funct import create_user
from application.misc.stocks_functions import create_track_price_object
from os import getenv


@pytest.fixture
def client():
    # engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')
    # Session = sessionmaker(engine)
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client


@pytest.fixture(scope="session")
def engine():
    return create_engine(getenv("SQLALCHEMY_DATABASE_URI"))


@pytest.fixture
def test_data_fixture(username_fixture, engine):
    Session = sessionmaker(engine)
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
            print(f'deleting user')


def test_user_creation(client, engine, username_fixture, test_data_fixture):
    Session = sessionmaker(engine)
    with Session() as session:
        user_to_create = session.query(Users). \
            filter(Users.username == username_fixture).one_or_none()
        assert user_to_create is not None
        print(user_to_create)


def test_Prices_tracking(client, engine, username_fixture, test_data_fixture):
    Session = sessionmaker(engine)
    with Session() as session:
        assert (create_track_price_object('kaka', test_data_fixture)) is not None
        assert (create_track_price_object('trtr', test_data_fixture)) is not None
    with Session() as session:
        price_track_obj = session.query(Prices_tracking). \
            filter(Prices_tracking.user_related == test_data_fixture).all()
        for alert in price_track_obj:
            print('price objects is', alert)
            assert alert is not None
            assert alert.user_related == test_data_fixture
        assert session.query(Prices_tracking). \
                   filter(Prices_tracking.user_related == test_data_fixture).count() == 2


def test_delete_alert_test_integrity(client, username_fixture, engine):
    Session = sessionmaker(engine)
    id_fix = create_user(username_fixture)
    id = create_track_price_object('kaka', id_fix)
    assert id is not None
    assert id_fix is not None
    with Session() as session:
        price_aler_obj = session.query(Prices_tracking). \
            filter(Prices_tracking.user_related == id_fix).one_or_none()
        assert price_aler_obj is not None
        session.delete(price_aler_obj)
        session.commit()
        user_check = session.query(Users). \
            filter(Users.id == id_fix).one_or_none()
        assert user_check is not None  # user still exists
        price_check = session.query(Prices_tracking). \
            filter(Prices_tracking.user_related == id_fix).one_or_none()
        assert price_check is None  # user still exists
        user_check = session.query(Users). \
            filter(Users.id == id_fix).one_or_none()
        session.delete(user_check)
        session.commit()


def test_acessing_valuess(client, engine, username_fixture, test_data_fixture):
    Session = sessionmaker(engine)
    id1 = create_track_price_object('kaka', test_data_fixture)
    id2 = create_track_price_object('gaga', test_data_fixture)
    assert id1 is not None
    assert id2 is not None
    with Session() as session:
        track_objects = session.query(Prices_tracking).all()
        for obj in track_objects:
            print('---------------=================-----------------')
            print('object exists:', obj)
        assert session.query(Prices_tracking).count() == 2
        user = session.query(Users). \
            filter(Users.id == test_data_fixture).one_or_none()
        assert user is not None
        all_tracking_obj = session.query(Prices_tracking). \
            join(Users). \
            filter(Prices_tracking.user_related == test_data_fixture). \
            all()
        for obj in all_tracking_obj:
            print('--------------', obj)
