import pytest
from unittest.mock import AsyncMock
from unittest import mock
from fastapi import HTTPException


def test_fetch_calendar_app_data_http_exception(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.AppData.get_calendar_app_data', new_callable=AsyncMock) as mock_get_calendar_app_data:
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


def test_fetch_calendar_app_data_server_failure(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.AppData.get_calendar_app_data', new_callable=AsyncMock) as mock_get_calendar_app_data:
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