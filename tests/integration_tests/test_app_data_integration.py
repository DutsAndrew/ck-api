import pytest

def test_fetch_calendar_app_data(test_client_with_db, generate_test_token):
    response = test_client_with_db.get(
    '/calendar',
    headers={
        'Accept': 'application/json',
        'Authorization': f'Bearer {generate_test_token}',
        'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 200
    assert 'detail' in json_response and json_response['detail'] == 'Calendar Data Loaded'
    assert 'data' in json_response

    data = json_response['data']
    assert '_id' in data
    assert data['app_data_type'] == 'calendar'
    assert 'calendar_dates' in data