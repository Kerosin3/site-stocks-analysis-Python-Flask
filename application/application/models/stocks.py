from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, PickleType

# import  application.models.database
# db = application.models.database.db
# from .database import db
# from application.models import db
from application.models.database import db
import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import registry
from application.misc.stocks_getter import get_data_for_plotting, get_today_price
import random
import pandas as pd


# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-one
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
# one to one
# mapper_registry = registry()
#

class Indexes(db.Model):
    __tablename__ = 'index_lists'
    # __mapper_args__ = {'eager_defaults',True}
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False, unique=True)
    index_value_today = Column(Integer, default=0, nullable=True, unique=False, server_default='0')
    index_value_yesterday = Column(Integer, default=0, nullable=True, unique=False, server_default='0')
    history_data = Column(PickleType, nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow,
                        server_default=func.now())
    changed_at = Column(DateTime, server_default=func.now(),
                        onupdate=datetime.datetime.utcnow)
    # index_id = Column(Integer, ForeignKey('index.id'))


# mapper_registry.map_imperatively(Indexes,Stock_data,Stock_one)
def create_index(ticker: str):
    out = None
    index = Indexes.query.filter_by(ticker=ticker).one_or_none()
    if index is None:
        out = Indexes()
        out.ticker = ticker
        data = get_data_for_plotting(ticker)
        out.index_value_today = get_today_price(ticker)
        out.index_value_yesterday = data['close'].iloc[-1]
        # out.index_value_yesterday = 5
        out.history_data = data
        # db.session.add(out)
        # db.session.commit()
    else:
        raise
    return out, data
