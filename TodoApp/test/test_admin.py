from .utils import *
from ..routers.admin import get_db,get_current_user
# from ..routers.todos import get_db
import pytest
from ..models import *
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_admin_read_all_authenticated(test_todo):
    resp = client.get("/admin/todo")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == [{"complete": False, "title": "learn fastapi", "description": "learn fastapi", "id": 1, "priority": 1, "owner_id": 1}]

def test_not_admin_read_all_authenticated(test_todo):
    resp = client.get("/admin/todo")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert resp.json() == {"detail": "You are not authorized to perform this action."}

def test_admin_delete_todo(test_todo):
    app.dependency_overrides[get_db] = override_get_db
    response = client.delete("/todos/1")
    assert response.status_code == status.HTTP_202_ACCEPTED
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None
