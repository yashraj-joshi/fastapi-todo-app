import os

import uvicorn
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# from sqlalchemy.ext.declarative import declarative_base

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
SQLALCHEMY_DATABASE_URL = os.environ['DATABASE_URL']
# engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread': False})
engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autoflush=True, autocommit=False, bind=engine)
Base = declarative_base()





