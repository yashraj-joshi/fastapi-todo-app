from typing import Annotated

import bcrypt
import pydantic
import uvicorn
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal,Base
from ..models import *
from .auth import get_current_user
from pydantic import SecretStr

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]


class UserVerification(BaseModel):
    old_password:Annotated[SecretStr,Field(min_length=8)]
    new_password:Annotated[SecretStr,Field(min_length=8)]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos(db:db_dependency,user:user_dependency):
    current_user = db.query(User).filter(User.id == user.get("user_id")).first()
    if current_user is not None:
        return current_user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

@router.post("/change_pw", status_code=status.HTTP_200_OK)
async def change_pw(db:db_dependency, user:user_dependency, uv:UserVerification):
    current_user = db.query(User).filter(User.id == user.get("user_id")).first()
    if current_user is not None:
        if not bcrypt.checkpw(uv.old_password.get_secret_value().encode(),current_user.hashed_password.encode()):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Old password is not correct")

        current_user.hashed_password = bcrypt.hashpw(uv.new_password.get_secret_value().encode(), bcrypt.gensalt()).decode()
        db.commit()
        db.refresh(current_user)
        return current_user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

@router.put("/update_phone_number", status_code=status.HTTP_200_OK)
async def update_phone_number(db:db_dependency, user:user_dependency, phone_number:str):
    current_user = db.query(User).filter(User.id == user.get("user_id")).first()
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    else:
        current_user.phone_number = phone_number
        db.commit()
        db.refresh(current_user)
    return current_user

@router.get("/current_user", status_code=status.HTTP_200_OK)
async def fetch_current_user(user:user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    current_user = db.query(User).filter(User.id == user.get("user_id")).first()
    return current_user