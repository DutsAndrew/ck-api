import pytest
from mongomock import MongoClient
from fastapi.testclient import TestClient
from main import get_app

@pytest.fixture
def app():
    app = get_app()
    yield app

@pytest.fixture
def test_client(app):
    app = TestClient(app)
    return app

@pytest.fixture
def mock_db(app):
    mock_client = MongoClient()
    app.mongo_client = mock_client
    yield mock_client
    mock_client.close()