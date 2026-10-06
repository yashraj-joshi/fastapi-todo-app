from .utils import *
from ..routers.user import get_db,get_current_user
from fastapi import status
import pytest

app.dependency_overrides[get_db] = override_get_db


app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_logged_in_user(test_user):
    resp = client.get("/user/current_user")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json().get("username") == "codingwithyashtest"
    assert resp.json().get("role") == "admin"
    assert resp.json().get("id") == 1
    assert resp.json().get("is_active") == True
    assert resp.json().get("phone_number") == "732-208-4025"

def test_change_password_success(test_user):
    request_data = {"old_password":"testpass","new_password":"testpass2"}
    resp = client.post("/user/change_pw",json=request_data)
    assert resp.status_code == status.HTTP_200_OK
