from fastapi.testclient import TestClient
from ..main import app
from fastapi import status

client = TestClient(app)
def test_return_health_check():
    resp = client.get("/healthy")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {"status":"healthy"}