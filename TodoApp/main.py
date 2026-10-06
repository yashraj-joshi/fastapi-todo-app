import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette import status

from .database import engine
from .models import Base
from .routers import auth, todos, admin,user
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

app = FastAPI()
Base.metadata.create_all(engine)
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)

# templates = Jinja2Templates(directory="TodoApp/templates")
app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def test(request:Request):
    r =  RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)
    return r
    # return templates.TemplateResponse(request=request, name="home.html")

@app.get("/healthy")
def healthy():
    return {"status":"healthy"}

if __name__ == "__main__":
    uvicorn.run("TodoApp.main:app", host="127.0.0.1", port=8000, reload=True)