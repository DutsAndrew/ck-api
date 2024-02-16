import pytest

# @pytest.mark.skip(reason='Not implemented')
def test_fetch_calendar_app_data(test_client_with_db, generate_test_token):
    response = test_client_with_db.get(
        '/calendar',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
    )

    json_response = response.json()


    assert response.status_code == 200
    assert json_response['detail'] == 'Calendar Data Loaded'
    assert json_response['data']['app_data_type'] == 'calendar'
    assert 'calendar_dates' in json_response['data']


# @pytest.mark.skip(reason='Not implemented')
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


# @pytest.mark.skip(reason='Not implemented')
def test_create_new_calendar_adds_calendar_to_db(test_client_with_db, generate_test_token):
    response = test_client_with_db.post(
        '/calendar/uploadCalendar',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
        json={
            'calendarColor': 'test',
            'calendarName': 'test',
            'createdBy': 'test test',
            'authorizedUsers': [
                {
                    'user': {
                        'type': 'authorized',
                        '_id': '65c637416c0f0cc3d35698c2'
                    },
                },
            ],
            'viewOnlyUsers': [
                {
                      'user': {
                          'type': 'view_only',
                          '_id': '65c637416c0f0cc3d35698c2'
                      },
                },
            ],
        }
    )

    assert response.status_code == 200

    json_response = response.json()

    assert 'detail' in json_response and json_response['detail'] == 'Calendar created and all necessary users added'


# @pytest.mark.skip(reason='Not implemented')
def test_add_user_to_calendar_adds_user(test_client_with_db, generate_test_token):
    calendar_id = '65c637426c0f0cc3d35698c4'
    user_id = '656a49c2ecbf3c97e58a1d37'

    response = test_client_with_db.post(
        f'/calendar/{calendar_id}/addUser/{user_id}/authorized',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
    )

    assert response.status_code == 200

    json_response = response.json()

    assert 'detail' in json_response and json_response['detail'] == 'We successfully added user to your calendar'
    assert 'updated_calendar' in json_response