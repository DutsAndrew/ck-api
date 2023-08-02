import pytest
from fastapi.testclient import TestClient

# For when wanting to isolate tests:
# @pytest.mark.skip(reason='Not implemented')

def test_api_welcome(test_client: TestClient):
    response = test_client.get('/api/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Using the /api prefix please request the correct data needed'}

def test_no_api_signup(test_client: TestClient):
    response = test_client.post('/api/signup')
    assert response.status_code == 422

def test_accurate_api_signup(test_client_with_db: TestClient):
    '''Test that a user can be created and saved to the database.'''

    # mock user data
    user_data = {
      'email': 'new@gmail.com',
      'company': 'Microsoft',
      'first_name': 'Bob',
      'last_name': 'Gregory',
      'job_title': 'Software Developer',
      'password': 'circles101$',
      'confirm_password': 'circles101$'
    }

    response = test_client_with_db.post(
        '/api/signup',
        json=user_data,
        headers={'content-type': 'application/json'}
    )

    assert response.status_code == 200
    assert response.json()['message'] == 'Success, we created your account'
    assert response.json()['success'] == True
    assert response.json()['user'] == {
        'email': 'new@gmail.com',
        'first_name': 'Bob',
        'last_name': 'Gregory',
        'job_title': 'Software Developer',
        'company': 'Microsoft',
    }

def test_user_already_signed_up(test_client_with_db: TestClient):
    '''Test case for when a user has already been added'''

    # mock user data
    user_data = {
      'email': 'new@gmail.com',
      'company': 'Microsoft',
      'first_name': 'Bob',
      'last_name': 'Gregory',
      'job_title': 'Software Developer',
      'password': 'circles101$',
      'confirm_password': 'circles101$'
  }

    response = test_client_with_db.post(
        '/api/signup',
        json=user_data,
        headers={'content-type': 'application/json'}
    )

    assert response.status_code == 200
    assert response.json()['message'] == 'That email is already registered with us, please login to your account or create one with a new email'
    assert response.json()['email'] == user_data['email']
    assert response.json()['company'] == user_data['company']
    assert response.json()['first_name'] == user_data['first_name']
    assert response.json()['job_title'] == user_data['job_title']
    assert response.json()['last_name'] == user_data['last_name']
    assert response.json()['password'] == user_data['password']

def test_sign_up_fails_on_no_data_entry(test_client_with_db: TestClient):
    '''Test case for when an account is being created but it's empty'''

    user_data = {
        
    }

    response = test_client_with_db.post(
        '/api/signup',
        json=user_data,
        headers={'content-type': 'application/json'}
    )

    assert response.status_code == 422

    # detail key is present from pydantic model validators
    assert 'detail' in response.json()
    assert isinstance(response.json()['detail'], list)

    # there should be 5 missing value errors
    errors = response.json()['detail']
    assert len(errors) == 5

    # Define the expected error types and corresponding field names
    expected_errors = [
        {'type': 'missing', 'field': 'email'},
        {'type': 'missing', 'field': 'company'},
        {'type': 'missing', 'field': 'first_name'},
        {'type': 'missing', 'field': 'last_name'},
        {'type': 'missing', 'field': 'password'},
    ]

    # loop through and make sure each error matches the expected errors above
    for i, error in enumerate(errors):
        assert 'type' in error
        assert 'loc' in error
        assert 'msg' in error

        # check if error type and field name match the expected values
        assert error['type'] == expected_errors[i]['type']
        assert error['loc'][1] == expected_errors[i]['field']