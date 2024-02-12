import pytest
from unittest.mock import AsyncMock
from unittest import mock
from fastapi import HTTPException


def test_fetch_calendar_data_user_lookup_fail(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.get_user_calendars', new_callable=AsyncMock) as mock_get_user_calendars:
        mock_get_user_calendars.side_effect = HTTPException(status_code=404, detail="User not found")

        response = test_client_with_db.get(
            '/calendar/getUserCalendarData',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            }
        )

        assert response.status_code == 404
        assert response.json()['detail'] == 'User not found'


def test_fetch_calendar_data_calendar_population_fail(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.fetch_all_user_calendars', new_callable=AsyncMock) as mock_populate_user_calendars:
        mock_populate_user_calendars.side_effect = HTTPException(status_code=422, detail="Failed to fetch all user calendars")

        response = test_client_with_db.get(
            '/calendar/getUserCalendarData',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            }
        )

        assert response.status_code == 422
        assert response.json()['detail'] == 'Failed to fetch all user calendars'