from sqlalchemy import Column, Integer, String,DateTime,Text,ForeignKey,PickleType
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship
from application.models.database import db
import datetime
from flask_wtf import FlaskForm
from .db_stocks import Stock_obj,Stock_data
from flask_login import UserMixin
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import InputRequired,Length,ValidationError

class Users(db.Model,UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow,
                        server_default=func.now())
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(80), nullable=False, unique=False)
    tickers_to_track = Column(PickleType, nullable=True) # to track

    # prices_alert = relationship('Prices_tracking',back_populates="user_related")
    prices_alert = relationship('Prices_tracking',cascade="all, delete-orphan",
                                back_populates="prices_to_track",uselist=False,passive_deletes=True)
    messanger0 = Column(String, nullable=True, unique=True)
    messanger1 = Column(String, nullable=True, unique=True)

    def __repr__(self):
        return f'Username:{self.username}, created at:{self.created_at}'

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(),
                                       Length(min=3,max=10)],
                         render_kw = {"placeholder": "Username"})
    password = StringField(validators=[InputRequired(),
                                       Length(min=4, max=10)],
                           render_kw={"placeholder": "Username"})
    submit = SubmitField("Register0")

    def validate_username(self,username):
        check_existing_user = Users.query.filter(username == username.data).one_or_none()
        print('checking user',check_existing_user)
        if check_existing_user is not None:
            raise ValidationError('user with this username is already registered')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),
                                       Length(min=3,max=10)],
                         render_kw = {"placeholder": "Username"})
    password = StringField(validators=[InputRequired(),
                                       Length(min=4, max=10)],
                           render_kw={"placeholder": "Username"})
    submit = SubmitField("Login1")
