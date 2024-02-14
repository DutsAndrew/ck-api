import pytest
from unittest.mock import AsyncMock, patch

@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
def test_remove_user_from_calendar_service_fails_on_no_user_or_calendar(
    mock_validate_user_and_calendar,
    test_client_with_db,
    generate_test_token,
):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'test_user_id'

    mock_validate_user_and_calendar.return_value = (None, None)

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/removeUserFromCalendar/{user_type}/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "This request cannot be processed"


@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
def test_remove_user_from_calendar_service_fails_on_no_user_or_calendar(
    mock_validate_user_and_calendar,
    test_client_with_db,
    generate_test_token,
):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'test_user_id'

    mock_validate_user_and_calendar.return_value = (
        {'_id': 'test_user_id'}, 
        {'_id': '123', 'created_by': 'test_user_id'}
    )


    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/removeUserFromCalendar/{user_type}/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "This request cannot be processed"


@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.has_calendar_permissions')
def test_remove_user_from_calendar_service_fails_on_no_user_has_no_permissions(
    mock_has_calendar_permissions,
    mock_validate_user_and_calendar,
    test_client_with_db,
    generate_test_token,
):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'test_user_id'

    mock_validate_user_and_calendar.return_value = (
        {'_id': 'test_user_id'}, 
        {'_id': '123', 'created_by': '456'}
    )
    mock_has_calendar_permissions.return_value = False

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/removeUserFromCalendar/{user_type}/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "This request cannot be processed"


@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.filter_out_user_from_calendar_list')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.has_calendar_permissions')
def test_remove_user_from_calendar_service_failed_to_filter_user(
    mock_has_calendar_permissions,
    mock_filter_out_user_from_calendar_list,
    mock_validate_user_and_calendar,
    test_client_with_db,
    generate_test_token,
):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'test_user_id'

    mock_validate_user_and_calendar.return_value = (None, None)
    mock_has_calendar_permissions.return_value = False
    mock_filter_out_user_from_calendar_list.return_value = None

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/removeUserFromCalendar/{user_type}/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "Failed to remove user"


@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.filter_out_user_from_calendar_list')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.has_calendar_permissions')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.replace_one_calendar', new_callable=AsyncMock)
def test_remove_user_from_calendar_service_failed_to_filter_user(
    mock_has_calendar_permissions,
    mock_filter_out_user_from_calendar_list,
    mock_replace_one_calendar,
    mock_validate_user_and_calendar,
    test_client_with_db,
    generate_test_token,
):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'test_user_id'

    mock_validate_user_and_calendar.return_value = ({'_id': '123'}, {'_id': '123', 'created_by': '456'})
    mock_has_calendar_permissions.return_value = True
    mock_filter_out_user_from_calendar_list.return_value = ({'_id': 'test'})
    mock_replace_one_calendar.return_value = None

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/removeUserFromCalendar/{user_type}/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "Failed to remove user"


@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.has_calendar_permissions')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.filter_out_user_from_calendar_list')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.replace_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.populate_one_calendar', new_callable=AsyncMock)
def test_remove_user_from_calendar_fails_on_failure_to_repopulate_calendar(
        mock_populate_one_calendar,
        mock_replace_one_calendar,
        mock_filter_out_user_from_calendar_list,
        mock_has_calendar_permissions,
        mock_validate_user_and_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'test_user_id'

    mock_validate_user_and_calendar.return_value = (
        {'_id': '123'}, 
        {'_id': '123', 'created_by': '456'}
    )
    mock_has_calendar_permissions.return_value = True
    mock_filter_out_user_from_calendar_list.return_value = ({'_id': '123'})
    mock_replace_one_calendar.return_value = ({'_id': '123'})
    mock_populate_one_calendar.return_value = None

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/removeUserFromCalendar/{user_type}/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "Failed to refetch updated calendar with removed user"


@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.has_calendar_permissions')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.filter_out_user_from_calendar_list')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.replace_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.populate_one_calendar', new_callable=AsyncMock)
def test_remove_user_from_calendar_succeeds(
        mock_populate_one_calendar,
        mock_replace_one_calendar,
        mock_filter_out_user_from_calendar_list,
        mock_has_calendar_permissions,
        mock_validate_user_and_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'test_user_id'

    mock_validate_user_and_calendar.return_value = (
        {'_id': '123'}, 
        {'_id': '123', 'created_by': '456'}
    )
    mock_has_calendar_permissions.return_value = True
    mock_filter_out_user_from_calendar_list.return_value = ({'_id': '123'})
    mock_replace_one_calendar.return_value = ({'_id': '123'})
    mock_populate_one_calendar.return_value = ({'_id': '123'})

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/removeUserFromCalendar/{user_type}/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 200
    assert json_response['detail'] == "User successfully removed from calendar"
    assert json_response['updated_calendar']['_id'] == '123'