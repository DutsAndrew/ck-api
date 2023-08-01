import pytest
from main import app

def test_api_welcome(test_client):
    response = test_client.get("/api/")
    assert response.status_code == 200
    assert response.json() == {'message': 'Using the /api prefix please request the correct data needed'}

def test_empty_api_signup(test_client):
    response = test_client.post("/api/signup")
    assert response.status_code == 422

def test_accurate_api_signup(test_client, mock_db):
    """Test that a user can be created and saved to the database."""

    user_data = {
        "email": "new@gmail.com",
        "company": "Microsoft",
        "first_name": "Bob",
        "last_name": "Krawzinski",
        "job_title": "Software Developer",
        "password": "circles101$",
    }

    response = test_client.post("/api/signup", json=user_data)
    assert response.json() == {"message": "Success, we created your account"}
    assert response.status_code == 200

    db = mock_db["db"]
    collection = db["users"]
    user_in_db = collection.find_one({"email": "new@gmail.com"})

    assert user_in_db is not None
    assert user_in_db["email"] == "new@gmail.com"