import pytest
import logging
from unittest.mock import AsyncMock, patch
from services.service_helpers.calendar_service_helpers import CalendarDataHelper

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


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
def test_add_user_to_calendar_fails_on_no_user_to_add_found(
        mock_validate_user_and_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = 'test_calendar_id'
    user_type = 'test_user_type'
    user_id = 'authorized'

    mock_validate_user_and_calendar.return_value = None

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
    assert json_response['detail'] == "There was an issue processing the user and calendar sent"


# @pytest.mark.skip(reason='Not implemented')
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.validate_user_and_calendar', new_callable=AsyncMock)
@patch('services.service_helpers.calendar_service_helpers.CalendarDataHelper.find_one_user', new_callable=AsyncMock)
def test_add_user_to_calendar_fails_on_no_user_to_add_found(
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
        {'_id': '456', 'created_by': '123'}
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
        {'_id': '123', 'created_by': '456'}
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
        {'_id': '123', 'created_by': '456'}
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
        {'_id': '123', 'created_by': '456'}
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
        {'_id': '123', 'created_by': '456'}
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
        {'_id': '123', 'created_by': '456'}
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
        {'_id': '123', 'created_by': '456'}
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
        mock_delete_one_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = '456'
    user_id = '123'

    mock_find_one_user.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = {'_id': '456', 'created_by': '123'}
    mock_group_all_user_ids_in_calendar.return_value = ['123', '322']
    mock_remove_calendar_from_users.return_value = 0
    mock_log_user_removal_status.return_value = f'When attempting to remove calendar from user instances, {mock_remove_calendar_from_users.return_value}\'s were not removed'
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
        mock_delete_one_calendar,
        test_client_with_db,
        generate_test_token,
    ):
    calendar_id = '456'
    user_id = '123'

    mock_find_one_user.return_value = {'_id': '123'}
    mock_find_one_calendar.return_value = {'_id': '456', 'created_by': '123'}
    mock_group_all_user_ids_in_calendar.return_value = ['123', '322']
    mock_remove_calendar_from_users.return_value = 0
    mock_log_user_removal_status.return_value = f'When attempting to remove calendar from user instances, {mock_remove_calendar_from_users.return_value}\'s were not removed'
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