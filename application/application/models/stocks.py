from sqlalchemy import Column, Integer, String,DateTime,Text
from .database import db
import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship
#https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-one
#https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
#one to one


class Stock_one(db.Model):
    __tablename__ = 'Stocks_list'
    __mapper_args__ = {'eager_defaults',True}
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False,unique=True)
    created_at = Column(DateTime,nullable=True,default=datetime.datetime.utcnow,
                        server_default=func.now())
    prices = relationship("Stock_data",back_populates = "stock_parent",
                          uselist=False )

class Stock_data(db.Model):
    __tablename__ = 'Stocks data'
    price = Column(Integer, nullable=True, unique=False, server_default='0')
    volume = Column(Integer, nullable=True, unique=False, server_default='0')
    on_date= Column(Text, nullable=True, unique=False, server_default='')
    stock_parent = relationship("Stock_one",back_populates='prices')
    array = db.Column(db.PickleType(mutable=True))

class Indexes(db.Model):
    __tablename__ = 'index_lists'
    __mapper_args__ = {'eager_defaults',True}
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False,unique=True)
    created_at = Column(DateTime,nullable=True,default=datetime.datetime.utcnow,
                        server_default=func.now())
    index_value = Column(Integer, nullable=True, unique=False, server_default='0')
