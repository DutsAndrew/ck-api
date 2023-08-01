import pytest
from fastapi.testclient import TestClient
from main import get_app, setup_db_client

app = get_app()
client = TestClient(app)

def test_app_get_welcome():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API"}