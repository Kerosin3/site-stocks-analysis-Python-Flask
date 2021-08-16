from sqlalchemy import Column, Integer, String,DateTime,Text,ForeignKey,PickleType
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship
from application.models.database import db
import datetime


class Stock_obj(db.Model):
    __tablename__ = 'Stocks_one'
    # __mapper_args__ = {'eager_defaults',True}
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False,unique=True)

    prices = relationship("Stock_data",back_populates = "stock_parent",
                          uselist=False )
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow,
                        server_default=func.now())
    changed_at = Column(DateTime, server_default=func.now(),
                        onupdate=datetime.datetime.utcnow)

class Stock_data(db.Model):
    __tablename__ = 'Stocks_data'
    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=True, unique=False, server_default='0')
    volume = Column(Integer, nullable=True, unique=False, server_default='0')
    on_date= Column(Text, nullable=True, unique=False, server_default='')

    stock_parent_id = Column(Integer, ForeignKey('Stocks_one.id'))
    stock_parent = relationship('Stock_one',back_populates = "prices")
    # array = db.Column(db.PickleType(mutable=True))
