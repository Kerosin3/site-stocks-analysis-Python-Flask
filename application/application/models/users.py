from sqlalchemy import Column, Integer, String,DateTime,Text,ForeignKey,PickleType
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship
from application.models.database import db
import datetime
from .db_stocks import Stock_obj,Stock_data

class Users(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow,
                        server_default=func.now())
    username = Column(String, nullable=False, unique=True)
    tickers_to_track = Column(PickleType, nullable=True) # to track

    # prices_alert = relationship('Prices_tracking',back_populates="user_related")
    prices_alert = relationship('Prices_tracking',cascade="all, delete-orphan",
                                back_populates="prices_to_track",uselist=False,passive_deletes=True)
    messanger0 = Column(String, nullable=True, unique=True)
    messanger1 = Column(String, nullable=True, unique=True)

