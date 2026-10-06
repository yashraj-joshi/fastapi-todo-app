import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette import status

from ..database import Base
from ..models import *
from ..main import app
import pytest
from fastapi.testclient import TestClient


SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL
                       , connect_args={"check_same_thread": False}
                       ,poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"username": "codingwithrobytest", "user_id": "1","role":"admin"}


client = TestClient(app)

@pytest.fixture()
def test_todo():
    todo = Todos(
        title="learn fastapi",
        description="learn fastapi",
        priority=1,
        complete=False,
        owner_id=1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield db
    db.query(Todos).delete()
    db.commit()

@pytest.fixture()
def test_user():
    user = User(username="codingwithyashtest", hashed_password=bcrypt.hashpw("testpass".encode("utf-8"),salt=bcrypt.gensalt()).decode("utf-8"),
                email="yash121293@gmail.com",
                role="admin", first_name="Yashraj",
                last_name="Joshi", phone_number="732-208-4025", is_active=True)
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    db.query(User).delete()
    db.commit()
