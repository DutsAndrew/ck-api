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
            'calendarName': 'test_for_developers_only_ck_api',
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


# @pytest.mark.skip(reason='Not implemented')
@pytest.mark.order(after='test_create_new_calendar_adds_calendar_to_db')
async def test_delete_calendar_succeeds(test_client_with_db, generate_test_token):
    calendar = await test_client_with_db.db['calendars'].find_one(
        {'name': 'test_for_developers_only_ck_api'}
    )

    calendar_id = calendar['_id']
    user_id = '65c637416c0f0cc3d35698c2'

    response = test_client_with_db.delete(
        f'/calendar/{calendar_id}/deleteCalendar/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
    )

    assert response.status_code == 200

    json_response = response.json()

    assert 'detail' in json_response and json_response['detail'] == 'Calendar successfully deleted'
    assert 'calendar_id' in json_response


# @pytest.mark.skip(reason='Not implemented')
@pytest.mark.order(before='test_delete_calendar_succeeds')
async def test_create_calendar_note_succeeds(test_client_with_db, generate_test_token):
    calendar = await test_client_with_db.db['calendars'].find_one(
        {'name': 'test_for_developers_only_ck_api'}
    )

    calendar_id = calendar['_id']

    response = test_client_with_db.post(
        f'/calendar/{calendar_id}/addNote',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
        json={
            'createdBy': 'test',
            'note': 'ck_api_test_note',
            'noteType': 'test',
            'dates': {
                'start_date': '2022-01-01 00:00:00',
                'end_date': '2022-01-01 23:59:59',
            },
        },
    )

    assert response.status_code == 200

    json_response = response.json()

    assert 'detail' in json_response and json_response['detail'] == 'Successfully updated calendar with note'
    assert 'updated_calendar' in json_response


# @pytest.mark.skip(reason='Not implemented')
@pytest.mark.order(before='test_delete_calendar_succeeds')
async def test_update_calendar_note_succeeds(test_client_with_db, generate_test_token):
    calendar = await test_client_with_db.db['calendars'].find_one(
        {'name': 'test_for_developers_only_ck_api'}
    )
    note = await test_client_with_db.db['calendar_notes'].find_one(
        {'name': 'ck_api_test_note'}
    )

    calendar_id = calendar['_id']
    note_id = note['_id']

    response = test_client_with_db.post(
        f'/calendar/{calendar_id}/updateNote/{note_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
        json={
            'createdBy': 'test',
            'note': 'ck_api_test_note',
            'noteType': 'test',
            'dates': {
                'start_date': '2022-01-01 00:00:00',
                'end_date': '2022-01-01 23:59:59',
            },
        },
    )

    assert response.status_code == 200

    json_response = response.json()

    assert 'detail' in json_response and json_response['detail'] == 'Successfully updated the note'
    assert 'updated_note' in json_response


# @pytest.mark.skip(reason='Not implemented')
@pytest.mark.order(after='test_create_calendar_note_succeeds')
async def test_delete_calendar_note_succeeds(test_client_with_db, generate_test_token):
    calendar = await test_client_with_db.db['calendars'].find_one(
        {'name': 'test_for_developers_only_ck_api'}
    )
    note = await test_client_with_db.db['calendar_notes'].find_one(
        {'name': 'ck_api_test_note'}
    )

    calendar_id = calendar['_id']
    note_id = note['_id']

    response = test_client_with_db.delete(
        f'/calendar/{calendar_id}/deleteNote/{note_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
    )

    assert response.status_code == 200

    json_response = response.json()

    assert 'detail' in json_response and json_response['detail'] == 'Success! Calendar was updated, note was removed'
    assert 'updated_calendar' in json_response


# @pytest.mark.skip(reason='Not implemented')
@pytest.mark.order(before='test_delete_calendar_succeeds')
async def test_post_calendar_event_succeeds(test_client_with_db, generate_test_token):
    calendar = await test_client_with_db.db['calendars'].find_one(
        {'name': 'test_for_developers_only_ck_api'}
    )

    calendar_id = calendar['_id']

    response = test_client_with_db.post(
        f'/calendar/{calendar_id}/createEvent',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
        json={
            'combinedDateAndTime': '2022-01-01 00:00:00',
            'date': '2022-01-01',
            'eventName': 'ck_api_test_event',
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
    assert 'updated_calendar' in response_json