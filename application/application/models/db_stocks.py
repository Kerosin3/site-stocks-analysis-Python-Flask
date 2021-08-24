from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, PickleType
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship
from application.models.database import db
import datetime


class Stock_obj(db.Model):
    __tablename__ = 'Stock_obj'
    # __mapper_args__ = {'eager_defaults',True}
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False, unique=True)
    comment = Column(String, nullable=True, unique=False)

    # prices = relationship("Stock_data",back_populates = "stock_parent",
    #                       uselist=False )
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow,
                        server_default=func.now())
    changed_at = Column(DateTime, server_default=func.now(),
                        onupdate=datetime.datetime.utcnow)
    # user_related = relationship("Users", back_populates="stock")
    # stock_data_ref = relationship("Stock_data", cascade="all,delete", back_populates="stock_obj_ref")
    # stock_ref_id = Column(Integer, ForeignKey('Stock_data.id'))
    Stock_data = relationship('Stock_data', backref='Stock_obj', lazy=True, uselist=False, cascade='delete')

    def __repr__(self):
        return f'Stock: ID:{self.id},ticker:{self.ticker},' \
               f'data of creation: {self.created_at}'


class Stock_data(db.Model):
    __tablename__ = 'Stock_data'
    id = Column(Integer, primary_key=True)
    today_price = Column(Integer, nullable=True, unique=False, server_default='0')

    Stock_obj_id = Column(Integer, ForeignKey('Stock_obj.id'), nullable=False)

    today_volume = Column(Integer, nullable=True, unique=False, server_default='0')
    historical_data = Column(PickleType, nullable=True)
    # Stock_obj_id = Column(Integer, ForeignKey('Stocks_obj.id'))
    # stock_obj_ref = relationship('Stock_obj',back_populates = "stock_data_ref")
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow,
                        server_default=func.now())
    changed_at = Column(DateTime, server_default=func.now(),
                        onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f'Stock data: {self.id}, {self.Stock_obj_id}, {self.created_at}'


class Prices_tracking(db.Model):
    __tablename__ = 'prices'
    # __mapper_args__ = {'eager_defaults',True}
    id = Column(Integer, primary_key=True)
    user_related = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    prices_to_track = relationship("Users", back_populates="prices_alert")
    ticker = Column(String, nullable=False, unique=True)
    price_alert_more = Column(Integer, nullable=True, unique=False)
    price_alert_less = Column(Integer, nullable=True, unique=False)

    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow,
                        server_default=func.now())
    changed_at = Column(DateTime, server_default=func.now(),
                        onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f'related user is {self.user_related},' \
               f'ticker to track: {self.ticker},' \
               f'updated at {self.created_at}'
    # user_related = relationship("Users", back_populates="stocks_track")
