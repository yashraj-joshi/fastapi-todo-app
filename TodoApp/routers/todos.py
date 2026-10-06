from typing import Annotated

import uvicorn
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal,Base
from ..models import Todos
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

templates = Jinja2Templates(directory="TodoApp/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TodoRequest(BaseModel):
    title: str = Field(min_length=1,max_length=100)
    description: str = Field(min_length=1,max_length=100)
    priority: int = Field(default=1,gt=0,lt=6)
    complete: bool = Field(False)

    model_config:ConfigDict= {
        "json_schema_extra":{
            "example":{
                "title":"title",
                "description":"description",
                "priority":"1",
                "complete":"True",
            }
        }
    }



db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

# region Pages
@router.get("/todo-page")
async def get_todos_page(request:Request,db:db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("user_id")).all()
        return templates.TemplateResponse(request,"todo.html",context={"todos":todos, "user":user})
    except Exception as e:
        print(e)
        return redirect_to_login()

@router.get("/add-todo-page")
async def get_add_todo_page(request:Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse(request,"add-todo.html")
    except Exception as e:
        print(e)
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def get_edit_todo_page(db:db_dependency,request:Request,todo_id:int):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        todo = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).first()
        return templates.TemplateResponse(request,"edit-todo.html",context={"todo":todo})
    except Exception as e:
        print(e)
        return redirect_to_login()

# @router.delete("/todo/{todo_id}",status_code=status.HTTP_202_ACCEPTED)
# async def delete_todo_obj( db:db_dependency,request:Request,todo_id:int):
#     try:
#         user = await get_current_user(request.cookies.get("access_token"))
#         if user is None:
#             return redirect_to_login()
#
#         Todo_obj = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).first()
#
#         if Todo_obj is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
#         db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).delete()
#         db.commit()
#
#     except Exception as e:
#         print(e)
#         return redirect_to_login()
#


# endregion

# region Endpoints
@router.get("/")
async def read_all(db:db_dependency, user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return db.query(Todos).all()

# @router.get("/todoid/{todo_id}",status_code=status.HTTP_200_OK)
# async def get_todo(db:db_dependency,todo_id:int = Path(gt=0)):
#     todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
#     if todo_model is not None:
#         return todo_model
#     else:
#         raise HTTPException(status_code=404, detail="Todo Not found.")

@router.get("/ids",status_code=status.HTTP_200_OK)
async def get_todo(db:db_dependency,
                   todo_id : Annotated[int,Path(gt=0,title="todo id")] | None = None,
                   user:user_dependency | None = None,
                   ):
    if todo_id is not None and user.get("user_id") is not None:
        todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id ==
                                            user.get("user_id")).first()
        return todo_model
    if todo_id is not None:
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
        return todo_model
    if user.get("user_id") is not None:
        todo_model = db.query(Todos).filter(Todos.owner_id == user.get("user_id")).all()
        return todo_model
    else:
        raise HTTPException(status_code=404, detail="Todo Not found.")

@router.get("/todo_id/{id}",status_code=status.HTTP_200_OK)
async def get_todo_by_id(db:db_dependency,user:user_dependency,id:int):
    todo = db.query(Todos).filter(Todos.owner_id == user.get("user_id")).filter(Todos.id == id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return  todo


@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_todos(request:TodoRequest, db:db_dependency, user:user_dependency):
    Todo_obj = Todos(**request.model_dump())
    Todo_obj.owner_id = user["user_id"]
    db.add(Todo_obj)
    db.commit()
    db.refresh(Todo_obj)
    return Todo_obj


@router.put("/{todo_id}",status_code=status.HTTP_202_ACCEPTED)
async def update_todo(request:TodoRequest, db:db_dependency,user:user_dependency,todo_id:int):
    Todo_obj = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("us er_id")).first()
    if Todo_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for key, value in request.model_dump().items():
        setattr(Todo_obj, key, value)
    setattr(Todo_obj, "owner_id", user.get("user_id"))
    db.commit()
    db.refresh(Todo_obj)  # Refreshes the object with any DB-generated fields
    return Todo_obj

@router.delete("/{todo_id}",status_code=status.HTTP_202_ACCEPTED)
async def delete_todo( db:db_dependency,user:user_dependency,todo_id:int):
    Todo_obj = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).first()

    if Todo_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).delete()
    db.commit()

# @router.post("/todos_page",status_code=status.HTTP_200_OK)
# async def get_todos_page(db:db_dependency,user:user_dependency,page:int=1,limit:int=10):
#     return "test"
#         # db.query(Todos).filter(Todos.owner_id == user.get("user_id")).offset((page-1)*limit).limit(limit).all()


# endregion
@router.get("/owner/",status_code=status.HTTP_200_OK)
async def get_current_user_todos(db:db_dependency,user:user_dependency):
    return db.query(Todos).filter(Todos.owner_id == user.get("user_id")).all()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)