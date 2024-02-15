import pytest
import certifi
import os
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from main import app as main_app
from dotenv import dotenv_values
from scripts.jwt_token_encoders import encode_bearer_token
from models.user import UserLogin

@pytest.fixture
def test_client():
    app = TestClient(main_app)
    return app


@pytest.fixture
def test_client_with_db():
    dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    config = dotenv_values(dotenv_path)
    
    mongodb_client = AsyncIOMotorClient(config["DEV_MONGO_URI"], tlsCAFile=certifi.where())
    db = mongodb_client[config["DEV_DB_NAME"]]

    # Inject the db instance into your FastAPI app
    main_app.mongodb_client = mongodb_client
    main_app.db = db

    app = TestClient(main_app)

    return app


@pytest.fixture(scope="session")
def generate_test_token():
    user_login = UserLogin(email="test@gmail.com", password="Test123$")

    bearer_token = encode_bearer_token(user_login=user_login)

    return bearer_token