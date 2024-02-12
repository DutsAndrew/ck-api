import pytest

def test_fetch_all_user_calendar_data(test_client_with_db, generate_test_token):
    response = test_client_with_db.get(
    '/calendar/getUserCalendarData',
    headers={
        'Accept': 'application/json',
        'Authorization': f'Bearer {generate_test_token}',
        'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 200
    assert 'detail' in json_response and json_response['detail'] == 'All possible calendars fetched'
    assert 'updated_user' in json_response

    user = json_response['updated_user']
    assert 'calendars' in user
    assert 'personal_calendar' in user
    assert 'pending_calendars' in user