from sqlalchemy import Column, Integer, String, Boolean,ForeignKey

from .database import Base

class Todos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True,nullable=False,index=True)
    title = Column(String,nullable=False)
    description = Column(String,nullable=False)
    priority = Column(Integer,nullable=False)
    complete = Column(Boolean,nullable=False,default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,nullable=False,index=True)
    email = Column(String,unique=True)
    username = Column(String,unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean,default=True)
    role=Column(String)
    phone_number=Column(String)

class Random_Table(Base):
    __tablename__ = 'random_table'
    id = Column(Integer, primary_key=True,nullable=False,index=True)
    name = Column(String)