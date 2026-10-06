
from ..routers.todos import get_db,get_current_user
from ..models import *
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "complete": False,
        "title": "learn fastapi",
        "description": "learn fastapi",
        "id": 1,
        "priority": 1,
        "owner_id": 1
    }]

def test_read_one_authenticated(test_todo):
    response = client.get("/todos/todo_id/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "complete": False,
        "title": "learn fastapi",
        "description": "learn fastapi",
        "id": 1,
        "priority": 1,
        "owner_id": 1
    }

def test_todo_not_found(test_todo):
    response = client.get("/todos/todo_id/999")
    assert response.status_code == 404
    assert response.json() == {"detail":"Todo not found"}


def test_create_todo(test_todo):
    request_data = {
        'title' : 'New Todo!',
        'description': 'New Todo Description',
        'priority': 5,
        'complete': False
    }
    response = client.post("/todos/",json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get("priority")

def test_update_todo(test_todo):
    request_data = {
        'title': 'New Todo!',
        'description': 'New Todo Description',
        'priority': 5,
        'complete': False
    }
    response = client.put("/todos/1",json=request_data)
    assert response.status_code == status.HTTP_202_ACCEPTED
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get("priority")

def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'New Todo!',
        'description': 'New Todo Description',
        'priority': 5,
        'complete': False
    }
    response = client.put("/todos/999",json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_todo(test_todo):
    response = client.delete("/todos/1")
    assert response.status_code == status.HTTP_202_ACCEPTED