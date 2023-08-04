import pytest
from fastapi.testclient import TestClient

# For when wanting to isolate tests:
# @pytest.mark.skip(reason='Not implemented')

def test_api_welcome(test_client: TestClient):
    response = test_client.get('/api/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Using the /api prefix please request the correct data needed'}

