from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from models.calendar import PendingUser, Calendar, CalendarNote, Event, UserRef
from services.app_data_services import AppData
from services.calendar_services import CalendarData
from services.service_helpers.calendar_service_helpers import CalendarDataHelper
from models.color_scheme import ColorScheme
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from datetime import datetime
from scripts.json_parser import json_parser
import logging
import asyncio

logger = logging.getLogger(__name__)

async def fetch_calendar_app_data(request: Request):
    calendar_app_data = await AppData.get_calendar_app_data(request)

    if isinstance(calendar_app_data, JSONResponse):
        return calendar_app_data
    
    if isinstance(calendar_app_data, HTTPException):
        return calendar_app_data
    
    return calendar_app_data
    

async def fetch_all_user_calendar_data(request: Request, user_email: str):
    user = await CalendarData.get_user_calendars_service(
        request, 
        user_email
    )

    if isinstance(user, JSONResponse):
        return user
            
    user_with_populated_calendars = await CalendarData.fetch_all_user_calendars_service(
        request, 
        user
    )
            
    if isinstance(user_with_populated_calendars, JSONResponse):
        return JSONResponse(content={'detail': 'Failed to fetch all user calendars'}, status_code=422)
    
    return JSONResponse(
        content={
            'detail': 'All possible calendars fetched',
            'updated_user': user_with_populated_calendars,
        }
    )
    

async def post_new_calendar(request: Request):
    new_calendar = await CalendarData.create_new_calendar_service(request=request)

    if 'calendar' in new_calendar:
        return JSONResponse(content={
            'detail': new_calendar['detail'],
            'calendar': jsonable_encoder(new_calendar['calendar']),
        }, status_code=200)
    else:
        return JSONResponse(content={'detail': new_calendar['detail']}, status_code=422)
    
    
async def remove_user_from_calendar(
        request: Request,
        calendar_id: str, 
        user_type: str, 
        user_id: str, 
        user_email: str
    ):
        return await CalendarData.remove_user_from_calendar_service(
            request,
            calendar_id,
            user_type,
            user_id,
            user_email,
        )


async def add_user_to_calendar(
        request: Request, 
        calendar_id: str, 
        user_id: str, 
        permission_type: str, 
        user_email: str
    ):
        return await CalendarData.add_user_to_calendar_service(
            request, 
            calendar_id, 
            user_id, 
            permission_type, 
            user_email,
        )
        

async def delete_calendar(
        request: Request, 
        calendar_id: str, 
        user_id: str
    ):
        return await CalendarData.delete_calendar_service(
            request, 
            calendar_id,
            user_id
        )


async def user_leave_calendar_request(
        request, 
        calendar_id, 
        user_id
    ):
        return await CalendarData.user_leave_calendar_service(
            request, 
            calendar_id, 
            user_id,
        )
    

async def post_note(
        request: Request, 
        calendar_id: str, 
        user_email: str
    ):
        return await CalendarData.post_note_service(
            request, 
            calendar_id, 
            user_email
        )
    

async def update_note(
        request: Request, 
        calendar_id: str, 
        note_id: str, 
        user_email: str
    ):
        return await CalendarData.update_note_service(
            request, 
            calendar_id, 
            note_id, 
            user_email,
        )
        

async def delete_note(
        request: Request, 
        calendar_id: str, 
        calendar_note_id: str,
        user_email: str,
    ):
        return await CalendarData.delete_note_service(
            request, 
            calendar_id, 
            calendar_note_id,
            user_email,
        )


async def post_event(
          request: Request, 
          calendar_id: str, 
          user_email: str
    ):
        return await CalendarData.post_event_service(
            request, 
            calendar_id, 
            user_email,
        )


async def put_event(
        request: Request,
        calendar_id: str, 
        event_id: str, 
    ):
        user_ref_of_event = await build_event_creator_instance(request, event_id)

        if isinstance(user_ref_of_event, JSONResponse):
            return user_ref_of_event
        
        request_body = await json_parser(request=request)

        if isinstance(request_body, JSONResponse):
            return request_body
        
        edited_event = build_edited_event(request_body, calendar_id, user_ref_of_event, event_id)

        if isinstance(edited_event, JSONResponse):
            return edited_event
                
        upload_updated_event = await update_event_and_calendar(request, edited_event, event_id)

        if isinstance(upload_updated_event, JSONResponse):
            return upload_updated_event
        
        updated_calendar = await CalendarDataHelper.populate_one_calendar(request, calendar_id)

        if updated_calendar is None:
            return JSONResponse(content={'detail': 'there was an issue populating the calendar with the updated event'}, status_code=422)

        return JSONResponse(content={
            'detail': 'Success! We updated your event',
            'updated_calendar': updated_calendar,
        }, status_code=200)


async def build_event_creator_instance(request: Request, event_id: str):
    outdated_event = await request.app.db['events'].find_one({'_id': event_id})

    if outdated_event is None:
        return JSONResponse(content={'detail': 'event not found'}, status_code=404)

    user_ref = outdated_event['created_by']
    return user_ref


def build_edited_event(request_body: dict, calendar_id: str, user_ref_of_event: dict, event_id: str):
    compiled_user_ref = UserRef(
        first_name=user_ref_of_event['first_name'],
        last_name=user_ref_of_event['last_name'],
        user_id=user_ref_of_event['user_id'],
    )

    new_calendar = Event(
        calendar_id=calendar_id,
        combined_date_and_time=datetime.fromisoformat(request_body['combinedDateAndTime'].replace('Z', '+00:00')) 
            if request_body['combinedDateAndTime'] 
            else None,
        created_by=compiled_user_ref,
        event_date=datetime.strptime(request_body['date'], '%Y-%m-%d') if request_body['date'] else None,
        event_description=request_body['eventDescription'] if request_body['eventDescription'] else '',
        event_name=request_body['eventName'] if request_body['eventName'] else '',
        event_time=request_body['selectedTime'] if len(request_body['selectedTime']) > 0 else '',
        repeat_option=request_body['repeatOption'] if request_body['repeatOption'] else '',
        repeats=request_body['repeat'] if request_body['repeat'] else False,
        id=event_id
    )

    if new_calendar is None:
        return JSONResponse(content={'detail': 'we could not create your calendar event'}, status_code=422)

    return new_calendar


async def update_event_and_calendar(request: Request, edited_event: Event, event_id):
    print(edited_event)
    updated_event = await request.app.db['events'].replace_one(
        {'_id': event_id},
        jsonable_encoder(edited_event),
    )

    if updated_event is None:
        return JSONResponse(content={'detail': 'we could not update that event'}, status_code=422)
    
    return


async def delete_event(request: Request, calendar_id: str, event_id: str):
    calendar_ref_removal = await request.app.db['calendars'].update_one(
        {'_id': calendar_id},
        {'$pull': {'events': event_id}}
    )

    if calendar_ref_removal is None:
        return JSONResponse(content={'detail': 'failed to remove event from calendar'}, status_code=422)

    event_removal = await request.app.db['events'].delete_one({'_id': event_id})

    if event_removal is None:
        return JSONResponse(content={'detail': 'failed to remove event'}, status_code=422)

    updated_calendar = await CalendarDataHelper.populate_one_calendar(request, calendar_id)

    if updated_calendar is None:
        return JSONResponse(content={'detail': 'there was an issue populating the calendar with the removed event'}, status_code=422)

    return JSONResponse(content={
        'detail': 'Success! We deleted your event',
        'updated_calendar': updated_calendar,
    }, status_code=200)


async def update_user_permissions(
        request: Request,
        calendar_id: str,
        new_user_permissions: str,
        user_id: str,
    ):
        calendar = await request.app.db['calendars'].find_one({'_id': calendar_id})

        if calendar is None:
            return JSONResponse(content={'detail': 'that calendar could not be found'}, status_code=404)
        
        if calendar['created_by'] == user_id:
          return JSONResponse(content={'detail': 'you cannot change the permissions of the calendar creator'}, status_code=422)

        current_user_permissions = get_user_permissions_in_calendar(calendar, user_id)

        if current_user_permissions is None:
            return JSONResponse(content={'detail': 'that user does not belong to this calendar'}, status_code=422)
        
        user_permission_change_status = await change_user_calendar_permissions(
            request, 
            calendar_id,
            current_user_permissions,
            new_user_permissions,
            user_id
        )

        if isinstance(user_permission_change_status, JSONResponse):
            return user_permission_change_status
        
        repopulated_calendar = await CalendarDataHelper.populate_one_calendar(request, calendar_id)

        if repopulated_calendar is None:
            return JSONResponse(content={'detail': 'we failed to repopulate the calendar you requested to update'}, status_code=422)

        return JSONResponse(content={
            'detail': 'Success! We changed the user\'s permissions and repopulated the calendar',
            'updated_calendar': repopulated_calendar,
        }, status_code=200)


def get_user_permissions_in_calendar(calendar: Calendar, userId: str):
    if userId in calendar['authorized_users']:
        return 'authorized'
    
    if userId in calendar['view_only_users']:
        return 'view_only'

    for user_instance in calendar['pending_users']:
        if userId == user_instance['_id']:
            return 'pending'
        
    return None


async def change_user_calendar_permissions(
        request: Request,
        calendar_id: str,
        current_user_permissions: str,
        new_user_permissions: str,
        user_id: str,
    ):
        if current_user_permissions is new_user_permissions:
            return JSONResponse(content={'detail': 'cannot change user permissions to what they already are'}, status_code=422)

        permission_removal_status = await remove_user_permissions(
            request, 
            calendar_id, 
            current_user_permissions, 
            user_id
        )

        if isinstance(permission_removal_status, JSONResponse):
            return permission_removal_status
        
        permission_addition_status = await add_user_permissions(
            request,
            calendar_id,
            current_user_permissions,
            new_user_permissions,
            user_id
        )

        if isinstance(permission_addition_status, JSONResponse):
            return permission_addition_status
        


async def remove_user_permissions(
        request: Request, 
        calendar_id: str, 
        current_user_permissions: str, 
        user_id: str,
    ):
        if current_user_permissions == 'pending':
            pending_user_removal = await remove_pending_user_from_calendar(request, calendar_id, user_id)

            if isinstance(pending_user_removal, JSONResponse):
                return pending_user_removal
        else:
            non_pending_user_removal = await remove_non_pending_user_from_calendar(
                request, 
                calendar_id, 
                user_id, 
                current_user_permissions
            )

            if isinstance(non_pending_user_removal, JSONResponse):
                return non_pending_user_removal


async def remove_pending_user_from_calendar(request: Request, calendar_id: str, user_id: str):
    pending_users = await request.app.db['calendars'].find_one(
        {'_id': calendar_id},
        projection={
            'pending_users': 1,
        }
    )

    if pending_users is None:
        return JSONResponse(content={'detail': 'could not retrieve pending users'}, status_code=422)
    
    filtered_users = pending_users['pending_users']

    for user in filtered_users:
        if user['_id'] == user_id:
            filtered_users.remove(user)

    updated_pending_users = await request.app.db['calendars'].update_one(
        {'_id': calendar_id},
        {'$set': {'pending_users': filtered_users}}
    )

    if updated_pending_users is None:
        return JSONResponse(content={'detail': 'failed to update pending users list'}, status_code=422)


async def remove_non_pending_user_from_calendar(
        request: Request, 
        calendar_id: str, 
        user_id: str,
        current_user_permissions: str,
    ):
        calendar = await request.app.db['calendars'].update_one(
            {'_id': calendar_id},
            {'$pull': {f"{current_user_permissions}_users": user_id}}
        )

        if calendar is None:
            return JSONResponse(content={'detail': 'that user\'s permission could not be changed'}, status_code=422)
        
        return calendar


async def add_user_permissions(
        request: Request,
        calendar_id: str,
        current_user_permissions: str,
        new_user_permissions: str,
        user_id: str,
    ):
        # IF USER IS PENDING, USER MUST REMAIN PENDING BUT CHANGE PENDING TYPE
        if current_user_permissions == 'pending':
            pending_user = PendingUser(type=new_user_permissions, user_id=user_id)

            upload_pending_user = await request.app.db['calendars'].update_one(
                {'_id': calendar_id},
                {'$push': {'pending_users': jsonable_encoder(pending_user)}}
            )

            if upload_pending_user is None:
                return JSONResponse(content={'detail': 'failed to switch user to pending user'}, status_code=422)
            
            return upload_pending_user

        else:
            upload_non_pending_user = await request.app.db['calendars'].update_one(
                {'_id': calendar_id},
                {'$push': {f"{new_user_permissions}_users": user_id}}
            )

            if upload_non_pending_user is None:
                return JSONResponse(content={'detail': 'failed to switch user to pending user'}, status_code=422)
            
            return upload_non_pending_user
        

async def set_user_preferred_calendar_color(
        request: Request, 
        calendar_id: str,
        user_email: str,
    ):
        calendar = await request.app.db['calendars'].find_one({'_id': calendar_id})
        user = await request.app.db['users'].find_one({'email': user_email}, projection={
            '_id': 1,
            'user_color_preferences.calendars': 1,
        })

        if user is None or calendar is None:
            return JSONResponse(content={'detail': 'The user or calendar you sent could not be found'}, status_code=404)

        request_body = await json_parser(request=request)

        if isinstance(request_body, JSONResponse):
            return request_body
        
        preferred_color = request_body['preferredColor']

        if len(preferred_color) == 0:
            return JSONResponse(content={'detail': 'no preferred color sent'}, status_code=422)

        new_color_scheme = ColorScheme(object_id=calendar_id, background_color=preferred_color)

        color_preference_update = await set_preferred_calendar_color(request, user, new_color_scheme)

        if isinstance(color_preference_update, JSONResponse):
            return color_preference_update
        
        return JSONResponse(content={
            'detail': 'Success! We added your preferences',
            'preferredColor': jsonable_encoder(new_color_scheme),
        }, status_code=200)


async def set_preferred_calendar_color(request: Request, user: object, new_color_scheme: ColorScheme):
    
    # check if a color scheme is set, if so call function to replace the current color scheme
    user_color_preferences = user['user_color_preferences']['calendars']
    if user_color_preferences:
        for color_preference in user_color_preferences:
            if color_preference['object_id'] == new_color_scheme.object_id:
                update_preference = await replace_old_calendar_color_preference(
                    request, 
                    user['_id'], 
                    color_preference['object_id'],
                    new_color_scheme,
                )

                if isinstance(update_preference, JSONResponse):
                    return update_preference
                
                return update_preference

    update_user = await add_preferred_calendar_color_to_user(
        request,
        user['_id'],
        new_color_scheme,
    )

    if isinstance(update_user, JSONResponse):
        return update_user
    
    return update_user
    

async def replace_old_calendar_color_preference(
        request: Request, 
        user_id: str, 
        old_color_scheme_id: str, 
        new_color_scheme
    ):
        user_update = await request.app.db['users'].update_one(
            {'_id': user_id},
            {'$set': {f'user_color_preferences.calendars.$[query]': jsonable_encoder(new_color_scheme)}},
            array_filters=[{'query.object_id': old_color_scheme_id}]
        )

        if user_update is None:
            return JSONResponse(content={'detail': 'we failed to upload user preferences'}, status_code=422)

        return user_update


async def add_preferred_calendar_color_to_user(
        request: Request,
        user_id: str,
        new_color_scheme
    ):
        user_update = await request.app.db['users'].update_one(
            {'_id': user_id},
            {'$push': {'user_color_preferences.calendars': jsonable_encoder(new_color_scheme)}}
        )

        if user_update is None:
            return JSONResponse(content={'detail': 'we failed to upload user preferences'}, status_code=422)

        return user_update