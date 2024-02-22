import pytest
from unittest.mock import AsyncMock
from unittest import mock


# @pytest.mark.skip(reason='Not implemented')
def test_new_calendar_route_succeeds(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.create_new_calendar_service', new_callable=AsyncMock) as mock_create_new_calendar:
    
        mock_create_new_calendar.return_value = {
            '_id': '123', 
            'calendar': {'_id': '456'},
            'detail': 'Calendar created and all necessary users added',
        }

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

        assert response.status_code == 200
        assert response.json()['detail'] == 'Calendar created and all necessary users added'
        assert 'calendar' in response.json()


# @pytest.mark.skip(reason='Not implemented')
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


# @pytest.mark.skip(reason='Not implemented')
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


# @pytest.mark.skip(reason='Not implemented')
def test_add_user_to_calendar_route_succeeds(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.add_user_to_calendar_service', new_callable=AsyncMock) as mock_add_user_to_calendar_service:
    
        mock_add_user_to_calendar_service.return_value = {
            'detail': 'We successfully added user to your calendar',
            'updated_calendar': {'_id': '123'},
        }

        response = test_client_with_db.post(
            'calendar/123/addUser/456/authorized',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            },
        )

        assert response.status_code == 200
        assert response.json()['detail'] == 'We successfully added user to your calendar'
        assert 'updated_calendar' in response.json()


# @pytest.mark.skip(reason='Not implemented')
def test_add_calendar_note_to_calendar_route_succeeds(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.post_note_service', new_callable=AsyncMock) as mock_add_user_to_calendar_service:
    
        mock_add_user_to_calendar_service.return_value = {
            'detail': 'Successfully updated calendar with note',
            'updated_calendar': {'_id': '123'},
        }

        response = test_client_with_db.post(
            'calendar/123/addNote',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            },
            json={
                'createdBy': 'John Wick',
                'note': 'This is a note',
                'noteType': 'mischievous',
                'dates': {
                    'start_date': '2022-01-01 00:00:00',
                    'end_date': '2022-01-01 23:59:59',
                }
            }
        )

        assert response.status_code == 200
        assert response.json()['detail'] == 'Successfully updated calendar with note'
        assert 'updated_calendar' in response.json()


# @pytest.mark.skip(reason='Not implemented')
def test_add_calendar_note_to_calendar_route_fails_on_missing_data(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.post_note_service', new_callable=AsyncMock) as mock_add_user_to_calendar_service:
    
        mock_add_user_to_calendar_service.return_value = {
            'detail': 'Successfully updated calendar with note',
            'updated_calendar': {'_id': '123'},
        }

        response = test_client_with_db.post(
            'calendar/123/addNote',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            },
            json={
                'createdBy': 'John Wick',
                'noteType': 'mischievous',
                'dates': {
                    'start_date': '2022-01-01 00:00:00',
                    'end_date': '2022-01-01 23:59:59',
                }
            }
        )

        response_json = response.json()

        assert response.status_code == 422
        
        assert 'detail' in response_json
        detail = response_json['detail']
        assert isinstance(detail, list) and len(detail) == 1
        
        error = detail[0]
        assert error['type'] == 'missing'
        assert error['loc'] == ['body', 'note']
        assert error['msg'] == 'Field required'


# @pytest.mark.skip(reason='Not implemented')
def test_add_calendar_note_to_calendar_route_fails_on_extra_data_sent(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.post_note_service', new_callable=AsyncMock) as mock_add_user_to_calendar_service:
    
        mock_add_user_to_calendar_service.return_value = {
            'detail': 'Successfully updated calendar with note',
            'updated_calendar': {'_id': '123'},
        }

        response = test_client_with_db.post(
            'calendar/123/addNote',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            },
            json={
                'alligators': True,
                'createdBy': 'John Wick',
                'note': 'This is a note',
                'noteType': 'mischievous',
                'dates': {
                    'start_date': '2022-01-01 00:00:00',
                    'end_date': '2022-01-01 23:59:59',
                }
            }
        )

        response_json = response.json()

        assert response.status_code == 422
        
        assert 'detail' in response_json
        detail = response_json['detail']
        assert isinstance(detail, list) and len(detail) == 1
        
        error = detail[0]
        assert error['type'] == 'extra_forbidden'
        assert error['loc'] == ['body', 'alligators']
        assert error['msg'] == 'Extra inputs are not permitted'


# @pytest.mark.skip(reason='Not implemented')
def test_update_calendar_note_to_calendar_route_succeeds(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.update_note_service', new_callable=AsyncMock) as mock_add_user_to_calendar_service:
    
        mock_add_user_to_calendar_service.return_value = {
            'detail': 'Successfully updated the note',
            'updated_note': {'_id': '111'},
        }

        response = test_client_with_db.put(
            'calendar/123/updateNote/111',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            },
            json={
                'createdBy': 'John Wick',
                'note': 'This is a note',
                'noteType': 'mischievous',
                'dates': {
                    'start_date': '2022-01-01 00:00:00',
                    'end_date': '2022-01-01 23:59:59',
                }
            }
        )

        assert response.status_code == 200
        assert response.json()['detail'] == 'Successfully updated the note'
        assert 'updated_note' in response.json()


# @pytest.mark.skip(reason='Not implemented')
def test_post_event_succeeds(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.post_event_service', new_callable=AsyncMock) as mock_add_user_to_calendar_service:
    
        mock_add_user_to_calendar_service.return_value = {
            'detail': 'Success! We uploaded your event',
            'updated_calendar': {'_id': '123'},
        }

        response = test_client_with_db.post(
            'calendar/123/createEvent',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            },
            json={
                'combinedDateAndTime': '2022-01-01 00:00:00',
                'date': '2022-01-01',
                'eventName': 'Test Event',
                'eventDescription': 'This is a test event',
                'repeat': False,
                'repeatOption': 'none',
                'selectedCalendar': 'Personal Calendar',
                'selectedCalendarId': '123',
                'selectedTime': '00:00:00',
            }
        )

        response_json = response.json()

        assert response.status_code == 200
        assert response_json['detail'] == 'Success! We uploaded your event'


# @pytest.mark.skip(reason='Not implemented')
def test_post_event_fails_on_missing_data(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.post_event_service', new_callable=AsyncMock) as mock_add_user_to_calendar_service:
    
        mock_add_user_to_calendar_service.return_value = {
            'detail': 'Success! We uploaded your event',
            'updated_calendar': {'_id': '123'},
        }

        response = test_client_with_db.post(
            'calendar/123/createEvent',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            },
            json={
                'combinedDateAndTime': '2022-01-01 00:00:00',
                'eventName': 'Test Event',
                'eventDescription': 'This is a test event',
                'repeat': False,
                'repeatOption': 'none',
                'selectedCalendar': 'Personal Calendar',
                'selectedCalendarId': '123',
                'selectedTime': '00:00:00',
            }
        )

        response_json = response.json()

        assert response.status_code == 422
        assert response_json['detail'] == [
            {
                'type': 'missing',
                'loc': ['body', 'date'],
                'msg': 'Field required',
                'input': {
                    'combinedDateAndTime': '2022-01-01 00:00:00',
                    'eventName': 'Test Event',
                    'eventDescription': 'This is a test event',
                    'repeat': False,
                    'repeatOption': 'none',
                    'selectedCalendar': 'Personal Calendar',
                    'selectedCalendarId': '123',
                    'selectedTime': '00:00:00'
                },
                'url': 'https://errors.pydantic.dev/2.1/v/missing'
            }
        ]


# @pytest.mark.skip(reason='Not implemented')
def test_post_event_fails_on_extra_data_present(test_client_with_db, generate_test_token):
    with mock.patch('controllers.calendar_controller.CalendarData.post_event_service', new_callable=AsyncMock) as mock_add_user_to_calendar_service:
    
        mock_add_user_to_calendar_service.return_value = {
            'detail': 'Success! We uploaded your event',
            'updated_calendar': {'_id': '123'},
        }

        response = test_client_with_db.post(
            'calendar/123/createEvent',
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {generate_test_token}',
                'Content-type': 'application/json',
            },
            json={
                'a-fun-extra': 'bug bug bug',
                'combinedDateAndTime': '2022-01-01 00:00:00',
                'eventName': 'Test Event',
                'eventDescription': 'This is a test event',
                'repeat': False,
                'repeatOption': 'none',
                'selectedCalendar': 'Personal Calendar',
                'selectedCalendarId': '123',
                'selectedTime': '00:00:00',
            }
        )

        response_json = response.json()

        print(response_json)

        assert response.status_code == 422
        assert response_json['detail'] == [
            {
                'type': 'missing',
                'loc': ['body', 'date'],
                'msg': 'Field required',
                'input': {
                    'a-fun-extra': 'bug bug bug',
                    'combinedDateAndTime': '2022-01-01 00:00:00',
                    'eventName': 'Test Event',
                    'eventDescription': 'This is a test event',
                    'repeat': False,
                    'repeatOption': 'none',
                    'selectedCalendar': 'Personal Calendar',
                    'selectedCalendarId': '123',
                    'selectedTime': '00:00:00'
                },
                'url': 'https://errors.pydantic.dev/2.1/v/missing'
            },
            {
                'type': 'extra_forbidden',
                'loc': ['body', 'a-fun-extra'],
                'msg': 'Extra inputs are not permitted',
                'input': 'bug bug bug',
                'url': 'https://errors.pydantic.dev/2.1/v/extra_forbidden'
            }
        ]