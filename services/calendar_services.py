from fastapi import Request
from fastapi.responses import JSONResponse
import asyncio
import logging

logger = logging.getLogger(__name__)


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
        calendars = await CalendarHelper.populate_individual_calendars(request, user.get('calendars', []))
        pending_calendars = await CalendarHelper.populate_individual_calendars(request, user.get('pending_calendars', []))
        personal_calendar = await CalendarHelper.populate_individual_calendars(request, [user.get('personal_calendar')])

        if isinstance(calendars, JSONResponse) or isinstance(pending_calendars, JSONResponse) or isinstance(personal_calendar, JSONResponse):
            return JSONResponse(content={'detail': 'Error populating calendars'}, status_code=500)
                
        user['calendars'] = calendars
        user['pending_calendars'] = pending_calendars
        user['personal_calendar'] = personal_calendar

        return user


class CalendarHelper:
    

    @staticmethod
    async def get_calendars(request: Request, calendar_ids: list[str]):
        calendars = []
        async for calendar in request.app.db['calendars'].find({'_id': {'$in': calendar_ids}}):
            calendars.append(calendar)
        return calendars


    @staticmethod
    async def gather_user_and_event_data(request: Request, calendars):
        authorized_user_ids = set()
        view_only_user_ids = set()
        calendar_notes_ids = set()
        event_ids = set()

        for calendar in calendars:
            authorized_user_ids.update(calendar.get('authorized_users', []))
            view_only_user_ids.update(calendar.get('view_only_users', []))
            calendar_notes_ids.update(calendar.get('calendar_notes', []))
            event_ids.update(calendar.get('events', []))

        user_projection = {
            'first_name': 1,
            'last_name': 1,
            'email': 1,
            'job_title': 1,
            'company': 1,
        }

        authorized_users, view_only_users, calendar_notes, events = await asyncio.gather(
            request.app.db['users'].find({'_id': {'$in': list(authorized_user_ids)}}, projection=user_projection).to_list(None),
            request.app.db['users'].find({'_id': {'$in': list(view_only_user_ids)}}, projection=user_projection).to_list(None),
            request.app.db['calendar_notes'].find({'_id': {'$in': list(calendar_notes_ids)}}).to_list(None),
            request.app.db['events'].find({'_id': {'$in': list(event_ids)}}).to_list(None)
        )

        return authorized_users, view_only_users, calendar_notes, events


    @staticmethod
    async def update_calendars(request: Request, calendars, authorized_users, view_only_users, calendar_notes, events):
        user_projection = {
            'first_name': 1,
            'last_name': 1,
            'email': 1,
            'job_title': 1,
            'company': 1,
        }

        calendar_authorized_users_dict = {str(user['_id']): user for user in authorized_users}
        calendar_view_only_users_dict = {str(user['_id']): user for user in view_only_users}

        for calendar in calendars:
            authorized_user_ids = calendar.get('authorized_users', [])
            view_only_user_ids = calendar.get('view_only_users', [])
            pending_user_ids = [str(pending_user.get('_id')) for pending_user in calendar.get('pending_users', [])]

            pending_users = await request.app.db['users'].find({
                '_id': {'$in': pending_user_ids}},
                projection=user_projection
            ).to_list(None)

            pending_users_with_type = []
            for pending_user in calendar.get('pending_users'):
                matching_user = next((user for user in pending_users if user['_id'] == pending_user['_id']), None)
                if matching_user:
                    combined_data = {
                        'type': pending_user.get('type'),
                        'user': matching_user  # Add the populated user instance
                    }
                    pending_users_with_type.append(combined_data)
                else:
                    continue

            calendar['authorized_users'] = [
                calendar_authorized_users_dict.get(str(user_id)) for user_id in authorized_user_ids
            ]
            calendar['pending_users'] = pending_users_with_type
            calendar['view_only_users'] = [
                calendar_view_only_users_dict.get(str(user_id)) for user_id in view_only_user_ids
            ]
            calendar['calendar_notes'] = [calendar_note for calendar_note in calendar_notes if calendar_note['calendar_id'] == calendar['_id']]
            calendar['events'] = [event for event in events if event['calendar_id'] == calendar['_id']]

        return calendars


    @staticmethod
    async def populate_individual_calendars(request: Request, calendar_ids: list[str]):
        try:
            if len(calendar_ids) == 0: return []

            calendars = await CalendarHelper.get_calendars(request, calendar_ids)
            authorized_users, view_only_users, calendar_notes, events = await CalendarHelper.gather_user_and_event_data(request, calendars)
            updated_calendars = await CalendarHelper.update_calendars(request, calendars, authorized_users, view_only_users, calendar_notes, events)

            return updated_calendars
        except Exception as e:
            logger.error(f"Error populating calendars: {e}")
            return JSONResponse(content={'detail': 'Error populating calendars'}, status_code=500)