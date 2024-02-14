import pytest
from fastapi.testclient import TestClient

# @pytest.mark.skip(reason='Not implemented')
def test_app_get_welcome(test_client: TestClient):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API"}