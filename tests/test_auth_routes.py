import pytest
import jwt
import http.cookies
from fastapi.testclient import TestClient
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from scripts.jwt_helper_functions import get_jwt_env_variables

# @pytest.mark.skip(reason='Not implemented')
def test_no_api_signup(test_client: TestClient):
    response = test_client.post('/auth/signup')
    assert response.status_code == 422

# @pytest.mark.skip(reason='Not implemented')
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
        '/auth/signup',
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

# @pytest.mark.skip(reason='Not implemented')
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
        '/auth/signup',
        json=user_data,
        headers={'content-type': 'application/json'}
    )

    assert response.status_code == 200
    assert response.json()['message'] == 'That email is already registered with us, please login to your account or create one with a new email'
    assert response.json()['user'] == {
        'email': 'new@gmail.com',
        'company': 'Microsoft',
        'first_name': 'Bob',
        'job_title': 'Software Developer',
        'last_name': 'Gregory',
    }


# @pytest.mark.skip(reason='Not implemented')
def test_sign_up_fails_on_no_data_entry(test_client_with_db: TestClient):
    '''Test case for when an account is being created but it's empty'''

    user_data = {
        
    }

    response = test_client_with_db.post(
        '/auth/signup',
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


# @pytest.mark.skip(reason='Not implemented')
def test_login_gives_good_auth_message_on_valid_login(test_client_with_db: TestClient):
    '''Test case to ensure a good login sends the appropriate message'''
    # mock user data
    user_data = {
      'email': 'new@gmail.com',
      'password': 'circles101$',
    }
    
    response = test_client_with_db.post(
        '/auth/login',
        json=user_data,
        headers={'content-type': 'application/json'}
    )

    assert response.status_code == 200
    assert response.json()['message'] == 'You have been successfully logged in'


@pytest.mark.skip(reason='Not implemented')
def test_login_sends_good_bearer_token_on_valid_login(test_client_with_db: TestClient, monkeypatch):
    '''Test case for checking good refresh token is sent'''
    # mock user data
    user_data = {
      'email': 'new@gmail.com',
      'password': 'circles101$',
    }

    jwt_config = get_jwt_env_variables()
    
    response = test_client_with_db.post(
        '/auth/login',
        json=user_data,
        headers={'content-type': 'application/json'}
    )

    jwt_bearer_token = response.headers['Authorization'].split(" ")[1]

    try:
        decoded_token = jwt.decode(
            jwt_bearer_token,
            jwt_config["JWT_SECRET"],
            algorithms=jwt_config["JWT_ALGORITHM"]
        )

        # compare approximate expiring values on token
        bearer_token_exp = datetime.fromtimestamp(decoded_token.get('exp')) # should be 12 hours
        approximate_token_exp = datetime.utcnow() + timedelta(hours=11)
        assert bearer_token_exp > approximate_token_exp
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='The refresh token has expired')
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail='The refresh token is invalid')
    

@pytest.mark.skip(reason='Not implemented')
def test_login_sends_good_refresh_token_as_cookie_on_valid_login(test_client_with_db: TestClient):
    '''Test case to make sure good refresh token is sent'''
    # mock user data
    user_data = {
      'email': 'new@gmail.com',
      'password': 'circles101$',
    }

    jwt_config = get_jwt_env_variables()
    
    response = test_client_with_db.post(
        '/auth/login',
        json=user_data,
        headers={'content-type': 'application/json'}
    )

    # verify token is a str and was sent
    jwt_refresh_token = response.cookies.get('refresh_token')
    assert isinstance(jwt_refresh_token, str)

    # verify token expires appropriately
    decoded_token = jwt.decode(
        jwt_refresh_token,
        jwt_config['JWT_SECRET'],
        algorithms=jwt_config['JWT_ALGORITHM']
    )
    refresh_token_exp = datetime.fromtimestamp(decoded_token.get('exp'), tz=timezone.utc) # should be 30 mins
    approximate_exp_time = (datetime.utcnow() + timedelta(days=6)).replace(tzinfo=timezone.utc)
    assert refresh_token_exp > approximate_exp_time

    # check header fields of cookie to make sure they are secure
    cookie_header = response.headers['set-cookie']
    cookies = http.cookies.SimpleCookie()
    cookies.load(cookie_header)
    cookie = cookies.get('refresh_token')
    
    assert cookie is not None
    assert cookie['httponly'] is True
    assert cookie['secure'] is True
    assert cookie['samesite'] == 'Lax'


# @pytest.mark.skip(reason='Not implemented')
def test_bad_login_does_not_authenticate_invalid_email(test_client_with_db: TestClient):
    '''Test case to ensure non-existent emails dont' validate'''
    # mock user data
    user_data = {
      'email': 'notavalidemail@gmail.com',
      'password': 'circles101$',
    }
    
    response = test_client_with_db.post(
        '/auth/login',
        json=user_data,
        headers={'content-type': 'application/json'}
    )

    assert response.json()['message'] == 'There was a server error processing your request'
    assert response.json()['errors'] == {
        'status_code': 401,
        'detail': 'Invalid email or password',
        'headers': None
    }


# @pytest.mark.skip(reason='Not implemented')
def test_bad_login_does_not_authenticate_invalid_password(test_client_with_db: TestClient):
    '''Test case to ensure that mismatched passwords but validated emails don't send tokens'''
    # mock user data
    user_data = {
      'email': 'new@gmail.com',
      'password': 'squares101$',
    }
    
    response = test_client_with_db.post(
        '/auth/login',
        json=user_data,
        headers={'content-type': 'application/json'}
    )

    assert response.json()['message'] == 'There was a server error processing your request'
    assert response.json()['errors'] == {
        'status_code': 401,
        'detail': 'Invalid email or password',
        'headers': None
    }