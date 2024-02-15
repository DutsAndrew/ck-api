import pytest
from unittest.mock import AsyncMock
from unittest import mock
from fastapi import HTTPException

# @pytest.mark.skip(reason='Not implemented')
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


# @pytest.mark.skip(reason='Not implemented')
def test_fetch_calendar_data_user_lookup_succeeds(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.get_user_calendars', new_callable=AsyncMock) as mock_get_user_calendars, \
         mock.patch('controllers.calendar_controller.CalendarData.fetch_all_user_calendars', new_callable=AsyncMock) as mock_populate_user_calendars:
        
        mock_get_user_calendars.return_value = {'_id': '123'}
        mock_populate_user_calendars.return_value = {'_id': '123'}

        response = test_client_with_db.get(
            '/calendar/getUserCalendarData',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            }
        )

        assert response.status_code == 200
        assert response.json()['detail'] == 'All possible calendars fetched'
        assert 'updated_user' in response.json()


# @pytest.mark.skip(reason='Not implemented')
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


# @pytest.mark.skip(reason='Not implemented')
def test_create_new_calendar_throws_server_error(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.create_new_calendar', new_callable=AsyncMock) as mock_create_new_calendar:
        mock_create_new_calendar.side_effect = HTTPException(status_code=500, detail="Server error")

        response = test_client_with_db.post(
            'calendar/uploadCalendar',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            },
            json={
                'calendarColor': '#111111',
                'calendarName': 'Test Calendar',
                'createdBy': 'John Wick',
                'authorizedUsers': [
                    {
                        'type': 'authorized',
                        'user_id': '12345'
                    },
                ],
                'viewOnlyUsers': [
                    {
                        'type': 'view_only',
                        'user_id': '67890'
                    }
                ],
            }
        )

        assert response.status_code == 500
        assert response.json()['detail'] == 'Server error'


# @pytest.mark.skip(reason='Not implemented')
def test_create_new_calendar_throws_server_error(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.create_new_calendar', new_callable=AsyncMock) as mock_create_new_calendar:
        mock_create_new_calendar.side_effect = HTTPException(status_code=422, detail="unprocessable entity")

        response = test_client_with_db.post(
            'calendar/uploadCalendar',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            },
            json={
                'calendarColor': '#111111',
                'calendarName': 'Test Calendar',
                'createdBy': 'John Wick',
                'authorizedUsers': [
                    {
                        'type': 'authorized',
                        'user_id': '12345'
                    },
                ],
                'viewOnlyUsers': [
                    {
                        'type': 'view_only',
                        'user_id': '67890'
                    }
                ],
            }
        )

        assert response.status_code == 422
        assert response.json()['detail'] == 'unprocessable entity'


# @pytest.mark.skip(reason='Not implemented')
def test_create_new_calendar_throws_server_error(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.create_new_calendar', new_callable=AsyncMock) as mock_create_new_calendar:
        mock_create_new_calendar.side_effect = HTTPException(status_code=404, detail="Failed to find db item")

        response = test_client_with_db.post(
            'calendar/uploadCalendar',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            },
            json={
                'calendarColor': '#111111',
                'calendarName': 'Test Calendar',
                'createdBy': 'John Wick',
                'authorizedUsers': [
                    {
                        'type': 'authorized',
                        'user_id': '12345'
                    },
                ],
                'viewOnlyUsers': [
                    {
                        'type': 'view_only',
                        'user_id': '67890'
                    }
                ],
            }
        )

        assert response.status_code == 404
        assert response.json()['detail'] == 'Failed to find db item'