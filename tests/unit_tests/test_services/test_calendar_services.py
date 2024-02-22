import pytest
import logging
from unittest.mock import AsyncMock, patch
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# @pytest.mark.skip(reason='Not implemented')
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


# @pytest.mark.skip(reason='Not implemented')
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


# @pytest.mark.skip(reason='Not implemented')
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
        {'_id': '123'}, 
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
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


# @pytest.mark.skip(reason='Not implemented')
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

    mock_validate_user_and_calendar.return_value = (
        {'_id': '123'}, 
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
    )
    mock_has_calendar_permissions.return_value = True
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


# @pytest.mark.skip(reason='Not implemented')
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

    mock_validate_user_and_calendar.return_value = (
        {'_id': '123'}, 
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
    )
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


# @pytest.mark.skip(reason='Not implemented')
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
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
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


# @pytest.mark.skip(reason='Not implemented')
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
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
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


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
def test_add_user_to_calendar_fails_on_no_permissions(
        mock_validate_user_and_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = '456'
    user_type = 'authorized'
    user_id = '123'

    mock_validate_user_and_calendar.return_value = (
        None, 
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
    )

    response = test_client_with_db.post(
        f'calendar/{calendar_id}/addUser/{user_id}/{user_type}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "This request cannot be processed"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_add_user_to_calendar_fails_on_no_calendar_found(
        mock_find_one_user,
        mock_validate_user_and_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'authorized'

    mock_validate_user_and_calendar.return_value = (
        {'_id': '123'}, 
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
    )
    mock_find_one_user.return_value = None

    response = test_client_with_db.post(
        f'calendar/{calendar_id}/addUser/{user_id}/{user_type}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "The user to add cannot be found"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.has_calendar_permissions')
def test_add_user_to_calendar_fails_on_no_calendar_permissions(
        mock_has_calendar_permissions,
        mock_find_one_user,
        mock_validate_user_and_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'authorized'

    mock_validate_user_and_calendar.return_value = (
        {'_id': '123'}, 
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
    )
    mock_find_one_user.return_value = {'_id': '123'}
    mock_has_calendar_permissions.return_value = False

    response = test_client_with_db.post(
        f'calendar/{calendar_id}/addUser/{user_id}/{user_type}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "This request cannot be processed"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.has_calendar_permissions')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.add_user_to_calendar_users_list', new_callable=AsyncMock)
def test_add_user_to_calendar_fails_on_user_not_added_to_calendar_list(
        mock_add_user_to_calendar_users_list,
        mock_has_calendar_permissions,
        mock_find_one_user,
        mock_validate_user_and_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'authorized'

    mock_validate_user_and_calendar.return_value = (
        {'_id': '123'}, 
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
    )
    mock_find_one_user.return_value = {'_id': '123'}
    mock_has_calendar_permissions.return_value = True
    mock_add_user_to_calendar_users_list.return_value = None

    response = test_client_with_db.post(
        f'calendar/{calendar_id}/addUser/{user_id}/{user_type}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "There was an issue adding that user, either the user was already in the list, or we failed to update the list"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.has_calendar_permissions')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.add_user_to_calendar_users_list', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
def test_add_user_to_calendar_fails_on_no_calendar_return_on_update_find(
        mock_find_one_calendar,
        mock_add_user_to_calendar_users_list,
        mock_has_calendar_permissions,
        mock_find_one_user,
        mock_validate_user_and_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'authorized'

    mock_validate_user_and_calendar.return_value = (
        {'_id': '123'}, 
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
    )
    mock_find_one_user.return_value = {'_id': '123'}
    mock_has_calendar_permissions.return_value = True
    mock_add_user_to_calendar_users_list.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = None

    response = test_client_with_db.post(
        f'calendar/{calendar_id}/addUser/{user_id}/{user_type}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "Failed to refetch updated calendar with added user"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.has_calendar_permissions')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.add_user_to_calendar_users_list', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_is_in_calendar')
def test_add_user_to_calendar_fails_on_user_in_calendar_check_fail(
        mock_verify_user_is_in_calendar,
        mock_find_one_calendar,
        mock_add_user_to_calendar_users_list,
        mock_has_calendar_permissions,
        mock_find_one_user,
        mock_validate_user_and_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'authorized'

    mock_validate_user_and_calendar.return_value = (
        {'_id': '123'}, 
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
    )
    mock_find_one_user.return_value = {'_id': '123'}
    mock_has_calendar_permissions.return_value = True
    mock_add_user_to_calendar_users_list.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = {'_id': '123'}
    mock_verify_user_is_in_calendar.return_value = False

    response = test_client_with_db.post(
        f'calendar/{calendar_id}/addUser/{user_id}/{user_type}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "User was not added to calendar successfully"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.has_calendar_permissions')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.add_user_to_calendar_users_list', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_is_in_calendar')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.populate_one_calendar', new_callable=AsyncMock)
def test_add_user_to_calendar_fails_on_unpopulated_calendar_return(
        mock_populate_one_calendar,
        mock_verify_user_is_in_calendar,
        mock_find_one_calendar,
        mock_add_user_to_calendar_users_list,
        mock_has_calendar_permissions,
        mock_find_one_user,
        mock_validate_user_and_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'authorized'

    mock_validate_user_and_calendar.return_value = (
        {'_id': '123'}, 
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
    )
    mock_find_one_user.return_value = {'_id': '123'}
    mock_has_calendar_permissions.return_value = True
    mock_add_user_to_calendar_users_list.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = {'_id': '123'}
    mock_verify_user_is_in_calendar.return_value = True
    mock_populate_one_calendar.return_value = None

    response = test_client_with_db.post(
        f'calendar/{calendar_id}/addUser/{user_id}/{user_type}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "Failed to refetch updated calendar with added user"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.has_calendar_permissions')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.add_user_to_calendar_users_list', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_is_in_calendar')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.populate_one_calendar', new_callable=AsyncMock)
def test_add_user_to_calendar_succeeds(
        mock_populate_one_calendar,
        mock_verify_user_is_in_calendar,
        mock_find_one_calendar,
        mock_add_user_to_calendar_users_list,
        mock_has_calendar_permissions,
        mock_find_one_user,
        mock_validate_user_and_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'authorized'

    mock_validate_user_and_calendar.return_value = (
        {'_id': '123'}, 
        {'_id': '456', 'created_by': '999', 'authorized_users': ['123']}
    )
    mock_find_one_user.return_value = {'_id': '123'}
    mock_has_calendar_permissions.return_value = True
    mock_add_user_to_calendar_users_list.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = {'_id': '123'}
    mock_verify_user_is_in_calendar.return_value = True
    mock_populate_one_calendar.return_value = {'_id': '123'}

    response = test_client_with_db.post(
        f'calendar/{calendar_id}/addUser/{user_id}/{user_type}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 200
    assert json_response['detail'] == "We successfully added user to your calendar"
    assert 'updated_calendar' in json_response


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.delete_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_all_calendar_notes', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_all_calendar_events', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.log_user_removal_status')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_calendar_from_users', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.group_all_user_ids_in_calendar')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_delete_calendar_succeeds(
        mock_find_one_user,
        mock_find_one_calendar,
        mock_group_all_user_ids_in_calendar,
        mock_remove_calendar_from_users,
        mock_log_user_removal_status,
        mock_remove_all_calendar_events,
        mock_remove_all_calendar_notes,
        mock_delete_one_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = '456'
    user_id = '123'

    mock_find_one_user.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = {
        '_id': '456', 
        'created_by': '123',
        'events': ['123', '322'],
        'notes': ['123', '322'],
    }
    mock_group_all_user_ids_in_calendar.return_value = ['123', '322']
    mock_remove_calendar_from_users.return_value = 0
    mock_log_user_removal_status.return_value = f'When attempting to remove calendar from user instances, {mock_remove_calendar_from_users.return_value}\'s were not removed'
    mock_remove_all_calendar_events.return_value = 0
    mock_remove_all_calendar_notes.return_value = 0
    mock_delete_one_calendar.return_value = {'_id': '456'}

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/deleteCalendar/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 200
    assert json_response['detail'] == "Calendar successfully deleted"
    assert 'calendar_id' in json_response



# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.delete_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_all_calendar_notes', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_all_calendar_events', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.log_user_removal_status')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_calendar_from_users', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.group_all_user_ids_in_calendar')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_delete_calendar_fails_on_no_delete(
        mock_find_one_user,
        mock_find_one_calendar,
        mock_group_all_user_ids_in_calendar,
        mock_remove_calendar_from_users,
        mock_log_user_removal_status,
        mock_remove_all_calendar_events,
        mock_remove_all_calendar_notes,
        mock_delete_one_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = '456'
    user_id = '123'

    mock_find_one_user.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = {
        '_id': '456', 
        'created_by': '123',
        'events': ['123', '322'],
        'notes': ['123', '322'],
    }
    mock_group_all_user_ids_in_calendar.return_value = ['123', '322']
    mock_remove_calendar_from_users.return_value = 0
    mock_log_user_removal_status.return_value = f'When attempting to remove calendar from user instances, {mock_remove_calendar_from_users.return_value}\'s were not removed'
    mock_remove_all_calendar_events.return_value = 0
    mock_remove_all_calendar_notes.return_value = 0
    mock_delete_one_calendar.return_value = None

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/deleteCalendar/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "Failed to delete calendar"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_delete_calendar_fails_on_user_is_not_calendar_creator(
        mock_find_one_user,
        mock_find_one_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_id = 'authorized'

    mock_find_one_user.return_value = {'_id': '999'}
    mock_find_one_calendar.return_value = {'_id': '456', 'created_by': '123'}

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/deleteCalendar/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "You cannot delete this calendar as you are not it\'s creator"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_delete_calendar_fails_on_no_calendar_find(
        mock_find_one_user,
        mock_find_one_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_id = 'authorized'

    mock_find_one_user.return_value = {'_id': '999'}
    mock_find_one_calendar.return_value = None

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/deleteCalendar/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "Invalid data requested"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_delete_calendar_fails_on_no_user_find(
        mock_find_one_user,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_id = 'authorized'

    mock_find_one_user.return_value = None

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/deleteCalendar/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "Invalid data requested"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.handle_remove_user_from_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_calendar_from_user', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_user_leave_calendar_request_succeeds(
        mock_find_one_user,
        mock_find_one_calendar,
        mock_remove_calendar_from_user,
        mock_handle_remove_user_from_calendar,
        test_client_with_db,
        generate_test_token,
    ):

    calendar_id = '456'
    user_id = '123'

    mock_find_one_user.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = {
        '_id': '456', 
        'created_by': '999', 
        'authorized_users': ['123'],
        'view_only_users': ['000'],
    }
    mock_remove_calendar_from_user.return_value = {'_id': '123'}
    mock_handle_remove_user_from_calendar.return_value = {'_id': '456'}

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/leaveCalendar/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 200
    assert json_response['detail'] == "Successfully left calendar"
    assert 'calendar_id' in json_response


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.handle_remove_user_from_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_calendar_from_user', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_user_leave_calendar_request_fails_on_failure_to_remove_user_from_calendar(
        mock_find_one_user,
        mock_find_one_calendar,
        mock_remove_calendar_from_user,
        mock_handle_remove_user_from_calendar,
        test_client_with_db,
        generate_test_token,
    ):

    calendar_id = '456'
    user_id = '123'

    mock_find_one_user.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = {
        '_id': '456', 
        'created_by': '999', 
        'authorized_users': ['123'],
        'view_only_users': ['000'],
    }
    mock_remove_calendar_from_user.return_value = {'_id': '123'}
    mock_handle_remove_user_from_calendar.return_value = None

    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/leaveCalendar/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "Failed to complete removal"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_calendar_from_user', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_user_leave_calendar_request_fails_on_failure_to_remove_calendar_from_user(
        mock_find_one_user,
        mock_find_one_calendar,
        mock_remove_calendar_from_user,
        test_client_with_db,
        generate_test_token,
    ):

    calendar_id = '456'
    user_id = '123'

    mock_find_one_user.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = {
        '_id': '456', 
        'created_by': '999', 
        'authorized_users': ['123'],
        'view_only_users': ['000'],
    }
    mock_remove_calendar_from_user.return_value = None
    
    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/leaveCalendar/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "Failed to complete removal"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_user_leave_calendar_request_fails_on_no_calendar_found(
        mock_find_one_user,
        mock_find_one_calendar,
        test_client_with_db,
        generate_test_token,
    ):

    calendar_id = '456'
    user_id = '123'

    mock_find_one_user.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = None
    
    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/leaveCalendar/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "The user or calendar sent do not exist"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_user_leave_calendar_request_fails_on_no_user_found(
        mock_find_one_user,
        test_client_with_db,
        generate_test_token,
    ):

    calendar_id = '456'
    user_id = '123'

    mock_find_one_user.return_value = None
    
    response = test_client_with_db.delete(
        f'calendar/{calendar_id}/leaveCalendar/{user_id}',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        }
    )

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "The user or calendar sent do not exist"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.populate_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.add_note_to_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.create_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user_by_email', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_user_add_calendar_note_succeeds(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_user_by_email,
        mock_create_calendar_note,
        mock_add_note_to_calendar,
        mock_populate_one_calendar,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_user_by_email.return_value = {'_id': '123'}
    mock_create_calendar_note.return_value = {'_id': '111'}
    mock_add_note_to_calendar.return_value = {'_id': '111'}
    mock_populate_one_calendar.return_value = {'_id': '456'}

    response = test_client_with_db.post(
        f'calendar/123/addNote',
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

    json_response = response.json()

    assert response.status_code == 200
    assert json_response['detail'] == "Successfully updated calendar with note"
    assert 'updated_calendar' in json_response


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.populate_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.add_note_to_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.create_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user_by_email', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_user_add_calendar_note_fails_on_no_calendar_population(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_user_by_email,
        mock_create_calendar_note,
        mock_add_note_to_calendar,
        mock_populate_one_calendar,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_user_by_email.return_value = {'_id': '123'}
    mock_create_calendar_note.return_value = {'_id': '111'}
    mock_add_note_to_calendar.return_value = {'_id': '111'}
    mock_populate_one_calendar.return_value = None

    response = test_client_with_db.post(
        f'calendar/123/addNote',
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

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "Failed to refetch updated calendar with note"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.add_note_to_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.create_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user_by_email', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_user_add_calendar_note_fails_on_failure_to_add_note_to_calendar(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_user_by_email,
        mock_create_calendar_note,
        mock_add_note_to_calendar,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_user_by_email.return_value = {'_id': '123'}
    mock_create_calendar_note.return_value = {'_id': '111'}
    mock_add_note_to_calendar.return_value = JSONResponse({
        'detail': 'We could not update that calendar with your note'}, status_code=404
    )

    response = test_client_with_db.post(
        f'calendar/123/addNote',
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

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "We could not update that calendar with your note"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.create_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user_by_email', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_user_add_calendar_note_fails_on_creating_note(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_user_by_email,
        mock_create_calendar_note,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_user_by_email.return_value = {'_id': '123'}
    mock_create_calendar_note.return_value = JSONResponse(content={
        'detail': 'Failed to upload new note'}, status_code=422
    )

    response = test_client_with_db.post(
        f'calendar/123/addNote',
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

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "Failed to upload new note"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user_by_email', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_user_add_calendar_note_fails_on_no_user_found(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_user_by_email,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_user_by_email.return_value = JSONResponse(content={
        'detail': 'User not found'}, status_code=404
    )

    response = test_client_with_db.post(
        f'calendar/123/addNote',
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

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "User not found"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_user_add_calendar_note_fails_on_no_calendar_permissions(
        mock_verify_user_has_calendar_authorization,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = False

    response = test_client_with_db.post(
        f'calendar/123/addNote',
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

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "We could not validate permissions"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.update_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.handle_move_calendar_note_to_new_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.create_updated_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_update_calendar_note_succeeds(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_calendar_note,
        mock_create_updated_note,
        mock_handle_move_calendar_note_to_new_calendar,
        mock_update_calendar_note,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_calendar_note.return_value = {'_id': '111', 'calendar_id': '456'}
    mock_create_updated_note.return_value = {'_id': '111'}
    mock_handle_move_calendar_note_to_new_calendar.return_value = {'_id': '555'}
    mock_update_calendar_note.return_value = {'_id': '111'}

    response = test_client_with_db.put(
        f'calendar/456/updateNote/111',
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

    json_response = response.json()

    assert response.status_code == 200
    assert json_response['detail'] == "Successfully updated the note"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.update_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.handle_move_calendar_note_to_new_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.create_updated_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_update_calendar_note_fails_on_calendar_note_not_updated(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_calendar_note,
        mock_create_updated_note,
        mock_handle_move_calendar_note_to_new_calendar,
        mock_update_calendar_note,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_calendar_note.return_value = {'_id': '111', 'calendar_id': '456'}
    mock_create_updated_note.return_value = {'_id': '111'}
    mock_handle_move_calendar_note_to_new_calendar.return_value = {'_id': '555'}
    mock_update_calendar_note.return_value = JSONResponse({
        'detail': 'Failed to update note'
    }, status_code=422)

    response = test_client_with_db.put(
        f'calendar/456/updateNote/111',
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

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "Failed to update note"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.handle_move_calendar_note_to_new_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.create_updated_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_update_calendar_note_fails_on_failure_to_migrate_calendars(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_calendar_note,
        mock_create_updated_note,
        mock_handle_move_calendar_note_to_new_calendar,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_calendar_note.return_value = {'_id': '111', 'calendar_id': '456'}
    mock_create_updated_note.return_value = {'_id': '111'}

    # THIS IS ONLY TESTING THE FAILURE TO REMOVE FROM ORIGINAL CALENDAR
    # DID NOT WRITE A SECOND TEST TO MOCK FAILURE TO ADD TO NEW CALENDAR AS IT WAS REDUNDANT
    mock_handle_move_calendar_note_to_new_calendar.return_value = JSONResponse({
        'detail': 'We failed to remove the note from that calendar'
    }, status_code=422)

    response = test_client_with_db.put(
        f'calendar/456/updateNote/111',
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

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "We failed to remove the note from that calendar"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.create_updated_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_update_calendar_note_fails_on_failure_to_create_updated_note(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_calendar_note,
        mock_create_updated_note,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_calendar_note.return_value = {'_id': '111', 'calendar_id': '456'}
    mock_create_updated_note.return_value = JSONResponse({
        'detail': 'The note you posted is not compatible'
    }, status_code=404)

    response = test_client_with_db.put(
        f'calendar/456/updateNote/111',
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

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "The note you posted is not compatible"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_update_calendar_note_fails_on_no_calendar_note_found(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_calendar_note,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_calendar_note.return_value = None

    response = test_client_with_db.put(
        f'calendar/456/updateNote/111',
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

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "That note could not be found"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_update_calendar_note_fails_on_no_calendar_permissions(
        mock_verify_user_has_calendar_authorization,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = JSONResponse({
        'detail': 'You do not have permission to update that note'
    }, status_code=404)

    response = test_client_with_db.put(
        f'calendar/456/updateNote/111',
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

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "We could not validate permissions"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.populate_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_note_from_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.delete_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_delete_note_service_succeeds(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_calendar,
        mock_find_one_calendar_note,
        mock_delete_note,
        mock_remove_note_from_calendar,
        mock_populate_one_calendar,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_calendar.return_value = {'_id': '456'}
    mock_find_one_calendar_note.return_value = {'_id': '111', 'calendar_id': '456'}
    mock_delete_note.return_value = {'_id': '111'}
    mock_remove_note_from_calendar.return_value = {'_id': '456'}
    mock_populate_one_calendar.return_value = {'_id': '456'}

    response = test_client_with_db.delete(
        f'calendar/456/deleteNote/111',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
    )

    json_response = response.json()

    assert response.status_code == 200
    assert json_response['detail'] == "Success! Calendar was updated, note was removed"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.populate_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_note_from_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.delete_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_delete_note_service_fails_on_no_populated_calendar(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_calendar,
        mock_find_one_calendar_note,
        mock_delete_note,
        mock_remove_note_from_calendar,
        mock_populate_one_calendar,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_calendar.return_value = {'_id': '456'}
    mock_find_one_calendar_note.return_value = {'_id': '111', 'calendar_id': '456'}
    mock_delete_note.return_value = {'_id': '111'}
    mock_remove_note_from_calendar.return_value = {'_id': '456'}
    mock_populate_one_calendar.return_value = None

    response = test_client_with_db.delete(
        f'calendar/456/deleteNote/111',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "we failed to populate an updated calendar without the note, but the note was removed"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.remove_note_from_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.delete_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_delete_note_service_fails_on_note_not_removed_from_calendar(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_calendar,
        mock_find_one_calendar_note,
        mock_delete_note,
        mock_remove_note_from_calendar,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_calendar.return_value = {'_id': '456'}
    mock_find_one_calendar_note.return_value = {'_id': '111', 'calendar_id': '456'}
    mock_delete_note.return_value = {'_id': '111'}
    mock_remove_note_from_calendar.return_value = JSONResponse({
        'detail': 'Failed to remove note from calendar'
    }, status_code=422)

    response = test_client_with_db.delete(
        f'calendar/456/deleteNote/111',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "Failed to remove note from calendar"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.delete_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_delete_note_service_fails_on_note_not_deleted(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_calendar,
        mock_find_one_calendar_note,
        mock_delete_note,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_calendar.return_value = {'_id': '456'}
    mock_find_one_calendar_note.return_value = {'_id': '111', 'calendar_id': '456'}
    mock_delete_note.return_value = JSONResponse({
        'detail': 'Failed to delete note'
    }, status_code=422)

    response = test_client_with_db.delete(
        f'calendar/456/deleteNote/111',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
    )

    json_response = response.json()

    assert response.status_code == 422
    assert json_response['detail'] == "Failed to delete note"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_delete_note_service_fails_on_no_note_found(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_calendar,
        mock_find_one_calendar_note,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_calendar.return_value = {'_id': '456'}
    mock_find_one_calendar_note.return_value = None

    response = test_client_with_db.delete(
        f'calendar/456/deleteNote/111',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
    )

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "Invalid data requested"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar_note', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_delete_note_service_fails_on_no_calendar_found(
        mock_verify_user_has_calendar_authorization,
        mock_find_one_calendar,
        mock_find_one_calendar_note,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = True
    mock_find_one_calendar.return_value = None
    mock_find_one_calendar_note.return_value = {'_id': '111'}

    response = test_client_with_db.delete(
        f'calendar/456/deleteNote/111',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
    )

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "Invalid data requested"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.verify_user_has_calendar_authorization', new_callable=AsyncMock)
def test_delete_note_service_fails_on_no_permissions(
        mock_verify_user_has_calendar_authorization,
        test_client_with_db,
        generate_test_token,
    ):

    mock_verify_user_has_calendar_authorization.return_value = False

    response = test_client_with_db.delete(
        f'calendar/456/deleteNote/111',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {generate_test_token}',
            'Content-type': 'application/json',
        },
    )

    json_response = response.json()

    assert response.status_code == 404
    assert json_response['detail'] == "We could not validate permissions"