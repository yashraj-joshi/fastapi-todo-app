from typing import Annotated

import uvicorn
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal,Base
from ..models import *
from .auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

@router.get("/todo", status_code=status.HTTP_200_OK)
async def get_all_todos(db:db_dependency,user:user_dependency):
    if user.get("role") == "admin":
        return db.query(Todos).all()
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not authorized to perform this action.")