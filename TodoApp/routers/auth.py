import os
from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form, Request
from pydantic import AliasChoices, BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal
from ..models import User
import bcrypt
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = 'HS256'

oauth2 = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    email: str
    firstName: str = Field(validation_alias=AliasChoices("firstName", "first_name", "firstname"))
    lastName: str = Field(validation_alias=AliasChoices("lastName", "last_name", "lastname"))
    password: Annotated[str, Field(min_length=8)]
    role: str
    phone_number: str
class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="TodoApp/templates")

def authenticate_user(username: str, password: str, db: db_dependency) -> User:
    user: User = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
        return False
    return user

# @router.api_route("/login-page", methods=["GET","POST"])
# async def render_login_page(request: Request):
#     if request.method == "GET":
#         return templates.TemplateResponse(request,"login.html")
#     elif request.method == "POST":
#         form_data = await request.form()
#         user = form_data.get("username")
#         pw = form_data.get("password")
#         lg = {"user": user, "pw": pw}
#         print(lg)
#         return templates.TemplateResponse(request,"login.html")
#     return None

@router.get("/login-page")
async def render_login_page(request: Request):
    return templates.TemplateResponse(request,"login.html")

@router.get("/register-page")
async def render_register_page(request: Request):
    return templates.TemplateResponse(request,"register.html")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    salt = bcrypt.gensalt()
    user = User(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.firstName,
        last_name=create_user_request.lastName,
        hashed_password=bcrypt.hashpw(create_user_request.password.encode("utf-8"), salt).decode("utf-8"),
        role=create_user_request.role,
        is_active=True,
        phone_number=create_user_request.phone_number
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



@router.post("/token",response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if user is not None and user is not False:
        if user.is_active:
            token = create_access_token(form_data.username, user.id, role=user.role,expires_delta=timedelta(minutes=30))
            return Token(access_token=token, token_type="bearer")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")



def create_access_token(username: str, user_id: int,role:str, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": username, "user_id": user_id,"role":role ,"exp": expires}

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username:str = payload.get("sub")
        user_id:int = payload.get("user_id")
        role:str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad token")
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    return {"username": username, "user_id": user_id,"role":role}

@router.post("/test")
async def test(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}
