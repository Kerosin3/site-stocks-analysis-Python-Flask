from os import environ, getenv
from config import TestingConfig
from sqlalchemy.orm import Session, sessionmaker, load_only, session
from sqlalchemy import create_engine

environ["FLASK_ENV"] = "TestingConfig"
# engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')
