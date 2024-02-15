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
    async def get_user_calendars(request: Request, user_email: str):
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
    async def fetch_all_user_calendars(request: Request, user):
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
    async def create_new_calendar(request: Request):
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
                user_email, calendar_id
            )

            if user is None or calendar is None:
              return JSONResponse(content={
                  'detail': 'There was an issue processing the user and calendar sent'}, status_code=404
            )

            user_to_add = CalendarDataHelper.find_one_user(
                request, 
                user_id
            )

            if user_to_add is None:
                return JSONResponse(content={'detail': 'The user to add cannot be found'}, status_code=404)
            
            if not CalendarDataHelper.has_calendar_permissions(
                user_email, 
                calendar
            ):
                return JSONResponse(content={
                    'detail': 'The user making that request is not authorized'}, status_code=422
                )
            
            updated_list = await CalendarDataHelper.add_user_to_calendar_users_list(
                request,
                user_id, 
                calendar, 
                permission_type, 
            )

            if updated_list is None:
                return JSONResponse(content={'detail': 'There was an issue adding that user, either the user was already in the list, or we failed to update the list'}, status_code=422)
            
            updated_calendar = await CalendarDataHelper.find_one_calendar(request, calendar_id)

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
                'updated_calendar': populated_calendar,
            }, status_code=200)
            
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)