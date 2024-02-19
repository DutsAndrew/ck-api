from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from scripts.json_parser import json_parser
from .service_helpers.calendar_service_helpers import CalendarDataHelper
import asyncio
import logging

logger = logging.getLogger(__name__)


# These methods interface directly with mongodb and call CalendarDataHelper methods 
# to prepare and manipulate the data for retrieval or storage
class CalendarData():

    @staticmethod
    async def get_user_calendars_service(request: Request, user_email: str):
        try:
            user = await request.app.db['users'].find_one(
                {"email": user_email},
                projection={
                    'calendars': 1,
                    'pending_calendars': 1,
                    'personal_calendar': 1,
                },
            )

            if user is None:
                return JSONResponse(content={'detail': 'User not found'}, status_code=404)
            
            return user
        
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def fetch_all_user_calendars_service(request: Request, user):
        try:
            calendars, pending_calendars, personal_calendar = await asyncio.gather(
                CalendarDataHelper.populate_individual_calendars(request=request, calendar_ids=user.get('calendars', [])),
                CalendarDataHelper. populate_individual_calendars(request=request, calendar_ids= user.get('pending_calendars', [])),
                CalendarDataHelper.populate_one_calendar(request=request, calendar_id=user.get('personal_calendar', None)),
            )

            if isinstance(calendars, JSONResponse) or isinstance(pending_calendars, JSONResponse) or personal_calendar is None:
                return JSONResponse(content={'detail': 'Error populating calendars'}, status_code=500)
                    
            user['calendars'] = calendars
            user['pending_calendars'] = pending_calendars
            user['personal_calendar'] = personal_calendar

            return user
        
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
    
    
    @staticmethod
    async def create_new_calendar_service(request: Request):
        try:
            request_body = await json_parser(request=request)

            if isinstance(request_body, JSONResponse):
                return request_body

            new_calendar, pending_users = CalendarDataHelper.create_calendar_instance(request_body)

            upload_status = await CalendarDataHelper.upload_new_calendar(
                request, 
                new_calendar, 
                pending_users, 
                request_body['createdBy']
            )

            return upload_status
        
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
    

    @staticmethod
    async def remove_user_from_calendar_service(
        request: Request, 
        calendar_id: str, 
        user_type: str,
        user_id: str, 
        user_email: str
    ):
        try:
            user, calendar = await CalendarDataHelper.validate_user_and_calendar(
                request, 
                user_email, 
                user_id,
                calendar_id
            )

            if (user is None or 
                calendar is None or 
                user_id == calendar['created_by'] or 
                user['_id'] not in calendar['authorized_users'] or
                not CalendarDataHelper.has_calendar_permissions(user, calendar)
                ):
                return JSONResponse(content={
                    'detail': 'This request cannot be processed'
                }, status_code=422)
            
            filtered_calendar = CalendarDataHelper.filter_out_user_from_calendar_list(user_id, calendar, user_type)

            if filtered_calendar is None:
                return JSONResponse(content={'detail': 'Failed to remove user'}, status_code=422)

            updated_calendar = await CalendarDataHelper.replace_one_calendar(
                request, 
                calendar_id, 
                filtered_calendar
            )

            if updated_calendar is None:
                return JSONResponse(content={'detail': 'Failed to update calendar to remove user'}, status_code=422)
            
            populated_calendar = await CalendarDataHelper.populate_one_calendar(request, calendar_id)

            if populated_calendar is None:
                return JSONResponse(content={'detail': 'Failed to refetch updated calendar with removed user'}, status_code=404)
            
            return JSONResponse(
                content={
                    'detail': 'User successfully removed from calendar',
                    'updated_calendar': jsonable_encoder(populated_calendar),
                },
                status_code=200
            )
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def add_user_to_calendar_service(
        request: Request, 
        calendar_id: str, 
        user_id: str, 
        permission_type: str, 
        user_email: str
    ):
        try:
            user, calendar = await CalendarDataHelper.validate_user_and_calendar(
                request, 
                user_email, 
                calendar_id
            )

            if (user is None or 
                calendar is None or 
                user_id == calendar['created_by'] or 
                user['_id'] not in calendar['authorized_users'] or
                not CalendarDataHelper.has_calendar_permissions(user, calendar)
                ):
                return JSONResponse(content={
                    'detail': 'This request cannot be processed'
                }, status_code=422)

            user_to_add = await CalendarDataHelper.find_one_user(
                request, 
                user_id
            )

            if user_to_add is None:
                return JSONResponse(content={'detail': 'The user to add cannot be found'}, status_code=404)
            
            updated_list = await CalendarDataHelper.add_user_to_calendar_users_list(
                request,
                user_id, 
                calendar, 
                permission_type, 
            )

            if updated_list is None:
                return JSONResponse(content={'detail': 'There was an issue adding that user, either the user was already in the list, or we failed to update the list'}, status_code=422)
            
            updated_calendar = await CalendarDataHelper.find_one_calendar(request, calendar_id)

            if updated_calendar is None:
                return JSONResponse(content={
                    'detail': 'Failed to refetch updated calendar with added user'}, status_code=404
                )
            
            if not CalendarDataHelper.verify_user_is_in_calendar(
                updated_calendar, 
                permission_type, user_id
            ):
                return JSONResponse(content={
                    'detail': 'User was not added to calendar successfully'}, status_code=422
                )
                                    
            populated_calendar = await CalendarDataHelper.populate_one_calendar(request, calendar_id)

            if populated_calendar is None:
                return JSONResponse(content={
                    'detail': 'Failed to refetch updated calendar with added user'}, status_code=404
                )
                        
            return JSONResponse(content={
                'detail': 'We successfully added user to your calendar',
                'updated_calendar': jsonable_encoder(populated_calendar),
            }, status_code=200)
            
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def delete_calendar_service(
        request: Request,
        calendar_id: str,
        user_id: str,
    ):
        try:
            user = await CalendarDataHelper.find_one_user(request, user_id)
            calendar = await CalendarDataHelper.find_one_calendar(request, calendar_id)

            if user is None or calendar is None:
                  return JSONResponse(content={
                      'detail': 'Invalid data requested'}, status_code=404
                  ) 
            
            if calendar['created_by'] != user_id:
                return JSONResponse(content={
                    'detail': 'You cannot delete this calendar as you are not it\'s creator'}, 
                    status_code=422
                )
            
            all_user_ids = CalendarDataHelper.group_all_user_ids_in_calendar(calendar, user['_id'])

            users_remove_status = 0
            if (len(all_user_ids) > 0):
                users_remove_status = await CalendarDataHelper.remove_calendar_from_users(
                    request, 
                    all_user_ids,
                    calendar_id
                )

            CalendarDataHelper.log_user_removal_status(users_remove_status)

            if (len(calendar['events']) > 0):
                await CalendarDataHelper.remove_all_calendar_events(
                    request,
                    calendar['events'],
                )

            if (len(calendar['notes']) > 0):
                await CalendarDataHelper.remove_all_calendar_notes(
                    request,
                    calendar['notes'],
                )

            delete_calendar = await CalendarDataHelper.delete_one_calendar(
                request,
                calendar_id,
            )

            if delete_calendar is None:
                return JSONResponse(content={
                    'detail': 'Failed to delete calendar'}, status_code=422
                )
            
            return JSONResponse(content={
                'detail': 'Calendar successfully deleted',
                'calendar_id': calendar_id,
            }, status_code=200)

        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def user_leave_calendar_service(
        request: Request, 
        calendar_id: str, 
        user_id: str
    ):
        try:
            user = await CalendarDataHelper.find_one_user(request, user_id)
            calendar = await CalendarDataHelper.find_one_calendar(request, calendar_id)

            if user is None or calendar is None:
                return JSONResponse(content={
                    'detail': 'The user or calendar sent do not exist'}, status_code=404
                )
            
            updated_user = await CalendarDataHelper.remove_calendar_from_user(
                request,
                user_id,
                calendar_id,
            )
            
            updated_calendar = await CalendarDataHelper.handle_remove_user_from_calendar(
                request,
                user_id,
                calendar_id,
                calendar['authorized_users'],
                calendar['view_only_users'],
            )

            if updated_user is None or updated_calendar is None:
                return JSONResponse(content={
                    'detail': 'Failed to complete removal'}, status_code=422
                )
            
            return JSONResponse(content={
                'detail': 'Successfully left calendar',
                'calendar_id': calendar_id,
            }, status_code=200)

        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)



    @staticmethod
    async def post_note_service(
        request: Request, 
        calendar_id: str, 
        user_email: str
    ):
        try:
            permissions = await CalendarDataHelper.verify_user_has_calendar_authorization(
                request, 
                user_email, 
                calendar_id
            )

            if permissions is False or isinstance(permissions, JSONResponse):
                return JSONResponse(content={
                    'detail': 'We could not validate permissions'}, status_code=404
                )

            user = await CalendarDataHelper.find_one_user_by_email(
                request,
                user_email,
                projection={
                    'first_name': 1,
                    'last_name': 1,
                    'personal_calendar': 1
                }
            )

            if isinstance(user, JSONResponse):
                return user

            calendar_note = await CalendarDataHelper.create_calendar_note(
                request, 
                user, 
                calendar_id
            )

            if isinstance(calendar_note, JSONResponse):
                return calendar_note
            
            updated_calendar = await CalendarDataHelper.add_note_to_calendar(
                request,
                calendar_id,
                calendar_note['_id'],
            )

            if isinstance(updated_calendar, JSONResponse):
                return updated_calendar
            
            populated_calendar = await CalendarDataHelper.populate_one_calendar(
                request,
                calendar_id,
            )

            if populated_calendar is None:
                return JSONResponse(content={
                    'detail': 'Failed to refetch updated calendar with note'}, status_code=404
                )
            
            return JSONResponse(content={
                'detail': 'Successfully updated calendar with note',
                'updated_calendar': jsonable_encoder(populated_calendar),
            }, status_code=200)
      
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def update_note_service(
        request: Request, 
        calendar_id: str, 
        note_id: str, 
        user_email: str
    ):
        try:
            permissions = await CalendarDataHelper.verify_user_has_calendar_authorization(
                request, 
                user_email, 
                calendar_id
            )

            if permissions is False or isinstance(permissions, JSONResponse):
                return JSONResponse(content={
                    'detail': 'We could not validate permissions'}, status_code=404
            )

            note = await CalendarDataHelper.find_one_calendar_note(
                request, 
                note_id,
            )

            if note is None:
                return JSONResponse(content={
                    'detail': 'That note could not be found'}, status_code=404
                )
            
            updated_note = await CalendarDataHelper.create_updated_note(
                request, 
                note, 
                calendar_id, 
            )

            if isinstance(updated_note, JSONResponse):
                return updated_note
            
            # move note to new calendar if necessary
            if note['calendar_id'] is not calendar_id:
                change_status = await CalendarDataHelper.handle_move_calendar_note_to_new_calendar(
                    request,
                    updated_note,
                    calendar_id,
                    note_id,                                                                   
                )

                if isinstance(change_status, JSONResponse):
                    return change_status
                
            uploaded_note = await CalendarDataHelper.update_calendar_note(
                request,
                updated_note,
                note_id
            )

            if isinstance(uploaded_note, JSONResponse):
                return uploaded_note
            
            return JSONResponse(content={
                'detail': 'Successfully updated the note',
                'updated_note': jsonable_encoder(updated_note),
            }, status_code=200)

        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        
  
    @staticmethod
    async def delete_note_service(
        request: Request,
        calendar_id: str,
        note_id: str,
        user_email,
    ):
        try:
            permissions = await CalendarDataHelper.verify_user_has_calendar_authorization(
                request, 
                user_email, 
                calendar_id
            )

            if permissions is False or isinstance(permissions, JSONResponse):
                return JSONResponse(content={
                    'detail': 'We could not validate permissions'}, status_code=404
            )
            
            calendar = await CalendarDataHelper.find_one_calendar(
                request, 
                calendar_id
            )

            note = await CalendarDataHelper.find_one_calendar_note(
                request,
                note_id,
            )

            if calendar is None or note is None:
                return JSONResponse(content={
                    'detail': 'Invalid data requested'}, status_code=404
                )
            
            note_deletion_status = await CalendarDataHelper.delete_note(
                request,
                note_id,
            )

            if isinstance(note_deletion_status, JSONResponse):
                return note_deletion_status

            note_removal_status = await CalendarDataHelper.remove_note_from_calendar(
                request,
                calendar_id,
                note_id,
            )

            if isinstance(note_removal_status, JSONResponse):
                return note_removal_status
            
            populated_calendar = await CalendarDataHelper.populate_one_calendar(
                request,
                calendar_id,
            )

            if populated_calendar is None:
                return JSONResponse(content={
                    'detail': 'we failed to populate an updated calendar without the note, but the note was removed'}, 
                status_code=422)
            
            return JSONResponse(content={
                'detail': 'Success! Calendar was updated, note was removed',
                'updated_calendar': populated_calendar,
            }, status_code=200)
        
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)