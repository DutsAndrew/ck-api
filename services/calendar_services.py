from fastapi import Request
from fastapi.responses import JSONResponse
from scripts import json_parser
from .service_helpers.calendar_service_helpers import CalendarDataHelper
import asyncio
import logging

logger = logging.getLogger(__name__)


# These methods interface directly with mongodb and call CalendarDataHelper methods 
# to prepare and manipulate the data for retrieval or storage
class CalendarData():

    @staticmethod
    async def get_user_calendars(request: Request, user_email: str):
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
        

    @staticmethod
    async def fetch_all_user_calendars(request: Request, user):
        
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
    
    
    @staticmethod
    async def create_new_calendar(request: Request):
        request_body = await json_parser(request=request)

        if isinstance(request_body, JSONResponse):
            return request_body

        new_calendar, pending_users = CalendarDataHelper.create_calendar_instance(request_body)

        return await CalendarDataHelper.upload_new_calendar(
            request, 
            new_calendar, 
            pending_users, 
            request_body['createdBy']
        )