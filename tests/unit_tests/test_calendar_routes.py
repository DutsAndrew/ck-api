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


def test_new_calendar_route_fails_with_missing_data(test_client_with_db, generate_test_token):
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
            # createdBy missing
            # authorizedUsers missing
            # viewOnlyUsers missing
        }
    )

    assert response.status_code == 422

    expected_response = {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "createdBy"],
                "msg": "Field required",
                "input": {"calendarColor": "#111111", "calendarName": "Test Calendar"},
                "url": "https://errors.pydantic.dev/2.1/v/missing"
            },
            {
                "type": "missing",
                "loc": ["body", "authorizedUsers"],
                "msg": "Field required",
                "input": {"calendarColor": "#111111", "calendarName": "Test Calendar"},
                "url": "https://errors.pydantic.dev/2.1/v/missing"
            },
            {
                "type": "missing",
                "loc": ["body", "viewOnlyUsers"],
                "msg": "Field required",
                "input": {"calendarColor": "#111111", "calendarName": "Test Calendar"},
                "url": "https://errors.pydantic.dev/2.1/v/missing"
            }
        ]
    }

    assert response.json() == expected_response


def test_new_calendar_route_fails_with_extra_fields(test_client_with_db, generate_test_token):
    response = test_client_with_db.post(
        'calendar/uploadCalendar',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
        json={
            'annotation': 'random junk',
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
            'extra_field': 'nonsensical stuff',
        }
    )

    assert response.status_code == 422

    expected_response = {
        'detail': [
            {
                'type': 'extra_forbidden',
                'loc': ['body', 'annotation'],
                'msg': 'Extra inputs are not permitted',
                'input': 'random junk',
                'url': 'https://errors.pydantic.dev/2.1/v/extra_forbidden'
            },
            {
                'type': 'extra_forbidden',
                'loc': ['body', 'extra_field'],
                'msg': 'Extra inputs are not permitted',
                'input': 'nonsensical stuff',
                'url': 'https://errors.pydantic.dev/2.1/v/extra_forbidden'
            }
        ]
    }

    assert response.json() == expected_response


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