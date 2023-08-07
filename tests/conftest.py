import pytest
import certifi
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from main import app as main_app
from dotenv import dotenv_values

@pytest.fixture
def test_client():
    app = TestClient(main_app)
    return app

@pytest.fixture
def test_client_with_db():
    # Use AsyncIOMotorClient for in-memory MongoDB
    config = dotenv_values(".env")
    mongodb_client = AsyncIOMotorClient(config["DEV_MONGO_URI"], tlsCAFile=certifi.where())
    db = mongodb_client[config["DEV_DB_NAME"]]

    # Inject the db instance into your FastAPI app
    main_app.mongodb_client = mongodb_client
    main_app.db = db

    app = TestClient(main_app)

    return app