import pytest
import asynctest
from fastapi import HTTPException

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


def test_fetch_calendar_app_data_http_exception(test_client_with_db, generate_test_token):
    with asynctest.patch('controllers.calendar_controller.AppData.get_calendar_app_data') as mock_get_calendar_app_data:
        mock_get_calendar_app_data.side_effect = HTTPException(status_code=404, detail="Calendar data not found")

        response = test_client_with_db.get(
            '/calendar',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            }
        )

        assert response.status_code == 404
        assert response.json()['detail'] == 'Calendar data not found'


def test_fetch_calendar_app_data_other(test_client_with_db, generate_test_token):
    with asynctest.patch('controllers.calendar_controller.AppData.get_calendar_app_data') as mock_get_calendar_app_data:
        mock_get_calendar_app_data.side_effect = HTTPException(status_code=500, detail="There was an issue processing your request")

        response = test_client_with_db.get(
            '/calendar',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            }
        )

        assert response.status_code == 500
        assert response.json()['detail'] == "There was an issue processing your request"