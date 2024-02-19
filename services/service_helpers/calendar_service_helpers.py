from fastapi import Request
from fastapi.responses import JSONResponse
from scripts import json_parser
from fastapi.encoders import jsonable_encoder
from models.calendar import Calendar, PendingUser, UserRef, CalendarNote, Event
from datetime import datetime
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class CalendarDataHelper:
    
    @staticmethod
    def handle_server_error(e: str):
        logger.error(f"Error processing request: {e}")
        return JSONResponse(
            content={
                'detail': 'There was an issue processing your request'
            }, status_code=500
        )
    
    @staticmethod
    async def get_calendars(request: Request, calendar_ids: list[str]):
        calendars = []
        async for calendar in request.app.db['calendars'].find({'_id': {'$in': calendar_ids}}):
            calendars.append(calendar)
        return calendars


    @staticmethod
    async def gather_calendar_field_data(request: Request, calendars):
        authorized_user_ids = set()
        view_only_user_ids = set()
        calendar_notes_ids = set()
        event_ids = set()

        for calendar in calendars:
            authorized_user_ids.update(calendar.get('authorized_users', []))
            view_only_user_ids.update(calendar.get('view_only_users', []))
            calendar_notes_ids.update(calendar.get('calendar_notes', []))
            event_ids.update(calendar.get('events', []))

        user_projection = UserProjection.user_projection

        authorized_users, view_only_users, calendar_notes, events = await asyncio.gather(
            request.app.db['users'].find({'_id': {'$in': list(authorized_user_ids)}}, projection=user_projection).to_list(None),
            request.app.db['users'].find({'_id': {'$in': list(view_only_user_ids)}}, projection=user_projection).to_list(None),
            request.app.db['calendar_notes'].find({'_id': {'$in': list(calendar_notes_ids)}}).to_list(None),
            request.app.db['events'].find({'_id': {'$in': list(event_ids)}}).to_list(None)
        )

        return authorized_users, view_only_users, calendar_notes, events


    @staticmethod
    async def attach_retrieved_calendar_fields_to_calendar(request: Request, calendars, authorized_users, view_only_users, calendar_notes, events):
        user_projection = UserProjection.user_projection

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

            calendars = await CalendarDataHelper.get_calendars(request, calendar_ids)
            authorized_users, view_only_users, calendar_notes, events = await CalendarDataHelper.gather_calendar_field_data(request, calendars)
            updated_calendars = await CalendarDataHelper.attach_retrieved_calendar_fields_to_calendar(request, calendars, authorized_users, view_only_users, calendar_notes, events)

            return updated_calendars
        except Exception as e:
            logger.error(f"Error populating calendars: {e}")
            return JSONResponse(content={'detail': 'Error populating calendars'}, status_code=500)
        
    
    @staticmethod
    def create_calendar_instance(request_body):
        pending_users = CalendarDataHelper.create_pending_user_instances(
            request_body['authorizedUsers'], 
            request_body['viewOnlyUsers']
        )

        new_calendar = Calendar(
            calendar_color=request_body['calendarColor'],
            calendar_type='team',
            name=request_body['calendarName'],
            user_id=request_body['createdBy'],
            pending_users=pending_users
        )

        return new_calendar, pending_users
        

    @staticmethod
    def create_pending_user_instances(authorized_users, view_only_users):
        pending_users = []

        # loop through and make all users in each list a pending user object for creating the calendar object
        for user in authorized_users:
            pending_user = PendingUser('authorized', user['user']['_id'])
            pending_users.append(pending_user)

        for user in view_only_users:
            pending_user = PendingUser('view_only', user['user']['_id'])
            pending_users.append(pending_user)

        return pending_users
    

    @staticmethod
    async def upload_new_calendar(request: Request, new_calendar: Calendar, pending_users, user_id: str):
        try:
            calendar_upload = await CalendarDataHelper.upload_calendar_to_db(request, new_calendar)
            calendar_id = str(calendar_upload.inserted_id)
            uploaded_calendar = await CalendarDataHelper.get_uploaded_calendar(request, calendar_id)
            updated_user_who_created_calendar = await CalendarDataHelper.update_user_calendars(request, user_id, calendar_id)

            if calendar_upload is None or uploaded_calendar is None or updated_user_who_created_calendar is None:
                return {
                    'detail': 'Failed to save, retrieve, and update calendar to user'
                }

            successful_users_updated, unsuccessful_users_updated = await CalendarDataHelper.update_pending_users(request, pending_users, calendar_id)

            if unsuccessful_users_updated > 0:
                return {
                    'calendar': uploaded_calendar,
                    'detail': 'Calendar created, all users were not invited successfully, please check the users and try again.',
                }
            
            if successful_users_updated == len(pending_users) or (successful_users_updated == 0 and unsuccessful_users_updated == 0):
                populated_calendar = await CalendarDataHelper.populate_one_calendar(request, calendar_id)
                if populated_calendar is None:
                    return {'detail': 'Calendar was not able to be populated'}
                
                return {
                  'detail': 'Calendar created and all necessary users added',
                  'calendar': populated_calendar,   
                }
            
            return {'detail': 'Something went wrong'}

        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)

    
    @staticmethod
    async def upload_calendar_to_db(request: Request, new_calendar: Calendar):
        try:
            calendar_upload = await request.app.db['calendars'].insert_one(jsonable_encoder(new_calendar))
            return calendar_upload
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)


    @staticmethod
    async def get_uploaded_calendar(request: Request, calendar_id: str):
        try:
            uploaded_calendar = await request.app.db['calendars'].find_one({'_id': calendar_id})
            return uploaded_calendar
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)


    @staticmethod
    async def update_user_calendars(request: Request, user_id: str, calendar_id: str):
        try:
            updated_user = await request.app.db['users'].update_one(
            {'_id': str(user_id)}, {'$push': {'calendars': calendar_id}})
            return updated_user
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)


    @staticmethod
    async def update_pending_users(request: Request, pending_users, calendar_id: str):
        successful_users_updated = 0
        unsuccessful_users_updated = 0

        for user in pending_users:
            update_user = await request.app.db['users'].find_one_and_update(
                {"_id": user.user_id}, {"$push": {"pending_calendars": calendar_id}}
            )

            if update_user is not None:
                successful_users_updated += 1
            else:
                unsuccessful_users_updated += 1

        return successful_users_updated, unsuccessful_users_updated
    

    @staticmethod
    async def populate_one_calendar(request: Request, calendar_id: str):
            
        calendar = await request.app.db['calendars'].find_one({'_id': calendar_id})
        
        if calendar is None:
            return None
        
        # set lists for storing ids for looking up in db
        authorized_user_ids = list(calendar.get('authorized_users', []))
        view_only_user_ids = list(calendar.get('view_only_users', []))
        pending_user_ids = [] # pending users are nested, need to loop through and retrieve id below
        calendar_note_ids = list(calendar.get('calendar_notes', []))
        event_ids = list(calendar.get('events', []))

        # pending users are nested, loop through to retrieve and store
        for pending_user in calendar.get('pending_users', []):
            user_id = pending_user.get('_id')
            if user_id:
                pending_user_ids.append(user_id)
        
        # entire user object should not be pulled, just grab these fields
        user_projection = UserProjection.user_projection

        # loop through and query ALL users for the following 3 lists
        authorized_users = await request.app.db['users'].find({
            '_id': {'$in': authorized_user_ids}},
            projection=user_projection
        ).to_list(None)
        view_only_users = await request.app.db['users'].find({
            '_id': {'$in': view_only_user_ids}},
            projection=user_projection
        ).to_list(None)
        pending_users = await request.app.db['users'].find({
            '_id': {'$in': pending_user_ids}},
            projection=user_projection
        ).to_list(None)
        calendar_notes = await request.app.db['calendar_notes'].find({
            '_id': {'$in': calendar_note_ids}
        }).to_list(None)
        events = await request.app.db['events'].find({
            '_id': {'$in': event_ids}
        }).to_list(None)

        # if any list fails return early as None as an error
        if authorized_users is None or view_only_users is None or pending_users is None or calendar_notes is None or events is None:
            return None

        # loop through and assign populated users back to their nested structure with type
        pending_users_with_type = []
        for pending_user in calendar.get('pending_users'):
            matching_user = next((user for user in pending_users if user['_id'] == pending_user['_id']), None)
            if matching_user:
                combined_data = {
                    'type': pending_user.get('type'),
                    'user': matching_user
                }
                pending_users_with_type.append(combined_data)

        # assign populated user objects back to calendar
        calendar['authorized_users'] = authorized_users
        calendar['view_only_users'] = view_only_users
        calendar['pending_users'] = pending_users_with_type
        calendar['calendar_notes'] = calendar_notes
        calendar['events'] = events
        
        return calendar
    

    @staticmethod
    async def validate_user_and_calendar(
        request: Request, 
        user_email: str,
        calendar_id: str
    ):
        try:
            user = await request.app.db['users'].find_one({'email': user_email})
            calendar = await request.app.db['calendars'].find_one({'_id': calendar_id})
            return user, calendar
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
    

    @staticmethod
    def has_calendar_permissions(user, calendar):
        return user is not None and (calendar['created_by'] == user['_id'] or user['_id'] in calendar['authorized_users'])
   
    
    @staticmethod
    def filter_out_user_from_calendar_list(
        user_id: str, 
        calendar, 
        user_type: str
    ):
        if user_type == 'authorized':
            calendar['authorized_users'].remove(user_id)
        elif user_type == 'pending':
            updated_pending_users = [user for user in calendar['pending_users'] if user['_id'] != user_id] # users are nested in pending list, need to loop through to modify
            calendar['pending_users'] = updated_pending_users
        elif user_type == 'view_only':
            calendar['view_only_users'].remove(user_id)
        else:
            return None # invalid type
        return calendar
    

    @staticmethod
    async def replace_one_calendar(
        request: Request, 
        calendar_id: str, 
        updated_calendar: dict
    ):
        try:
            return await request.app.db['calendars'].replace_one(
                {'_id': calendar_id},
                updated_calendar
            )
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
    

    @staticmethod
    async def find_one_calendar(
        request: Request,
        calendar_id: str,
        projection: Optional[dict] = None,
    ):
        try:
            return await request.app.db['calendars'].find_one(
                {'_id': calendar_id}, 
                projection
            )
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
    

    @staticmethod
    async def find_one_user(
        request: Request, 
        user_id: str,
        projection: Optional[dict] = None
    ):
        try:
            return await request.app.db['users'].find_one(
                {'_id': user_id}, 
                projection
            )
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
    

    @staticmethod
    async def find_one_user_by_email(
        request: Request, 
        user_email: str,
        projection: Optional[dict] = None
    ):
        try:
            user = await request.app.db['users'].find_one(
                {'email': user_email},
                projection
            )

            if user is None:
                return JSONResponse(content={
                    'detail': 'User not found'}, status_code=404
                )

        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
    

    @staticmethod
    async def add_one_user_to_calendar(
        request: Request, 
        calendar_id: str, 
        converted_user: dict
    ):
        try:
            return await request.app.db['calendars'].update_one(
                {'_id': calendar_id},
                {'$push': {'pending_users': converted_user}}
            )
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
    

    @staticmethod
    async def create_calendar_note(
        request: Request, 
        calendar_note: CalendarNote
    ):
        try:
            uploaded_note = await request.app.db['calendar_notes'].insert_one(
                jsonable_encoder(calendar_note)
            )

            if uploaded_note is None:
                return JSONResponse(content={
                    'detail': 'Failed to upload new note'}, status_code=422
                )
            
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
    

    @staticmethod
    async def find_calendar_note(request: Request, note_id: str):
        try:
            return await request.app.db['calendar_notes'].find_one({'_id': note_id})
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
    

    @staticmethod
    async def add_calendar_note_to_calendar(
        request: Request, 
        calendar_id: str, 
        note_id: str
    ):
        try:
            return await request.app.db['calendars'].update_one(
                {'_id': calendar_id},
                {'$push': {'calendar_notes': note_id}}
            )
        except Exception as e:  
            return CalendarDataHelper.handle_server_error(e)
    

    @staticmethod
    async def remove_calendar_from_user(
        request: Request,
        user_id: str,
        calendar_id: str,
    ):
        try:
            return await request.app.db['users'].update_one(
                {'_id': user_id},
                {'$pull': {'calendars': calendar_id}}
            )
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def remove_user_from_calendar(
        request: Request,
        user_id: str,
        calendar_id: str,
        calendar_type: str
    ):
        try:
            return await request.app.db['calendars'].update_one(
                {'_id': calendar_id},
                {'$pull': {calendar_type: user_id}}
            )
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def remove_all_calendar_events(
        request: Request, 
        calendar_events: list[str]
    ):
        removal_amount = len(calendar_events)

        try:
            event_removal_status = await request.app.db['events'].delete_many({
                '_id': {'$in': calendar_events}}
            )

            actual_removal_amount = event_removal_status.deleted_count

            if actual_removal_amount != removal_amount:
                CalendarDataHelper.log_event_removal_status(
                    removal_amount - actual_removal_amount
                )

            return

        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def remove_all_calendar_notes(
        request: Request,
        calendar_notes: list[str],
    ):
        removal_amount = len(calendar_notes)

        try:
            note_removal_status = await request.app.db['calendar_notes'].delete_many({
                '_id': {'$in': calendar_notes}}
            )

            actual_removal_amount = note_removal_status.deleted_count

            if actual_removal_amount != removal_amount:
                CalendarDataHelper.log_note_removal_status(
                    removal_amount - actual_removal_amount
                )

            return

        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def find_one_calendar_note(
        request: Request,
        note_id: str,
    ):
        try:
            note = await request.app.db['calendar_notes'].find_one(
                {'_id': note_id}
            )

            if note is None:
                return JSONResponse(content={
                    'detail': 'Note not found'}, status_code=404
                )

        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def update_calendar_note(
        request: Request,
        note_id: str,
        note: CalendarNote,
    ):
        try:
            uploaded_note = await request.app.db['calendar_notes'].update_one(
                {'_id': note_id},
                {'$set': jsonable_encoder(note)}
            )

            if uploaded_note is None:
                return JSONResponse(content={
                    'detail': 'Failed to update note'}, status_code=422
                )

        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def delete_note(
        request: Request,
        note_id: str,
    ):
        try:
            note_delete = await request.app.db['calendar_notes'].delete_one(
                {'_id': note_id}
            )

            if note_delete is None:
                return JSONResponse(content={
                    'detail': 'Failed to delete note'}, status_code=422
                )

        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def remove_note_from_calendar(
        request: Request,
        calendar_id: str,
        note_id: str,
    ):
        try:
            removal_status = await request.app.db['calendars'].update_one(
                {'_id': calendar_id},
                {'$pull': {'calendar_notes': note_id}}
            )

            if removal_status is None:
                return JSONResponse(content={
                    'detail': 'Failed to remove note from calendar'}, status_code=422
                )

        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)


    @staticmethod
    async def add_user_to_calendar_users_list(
        request: Request, 
        user_id: str, 
        calendar: Calendar, 
        type_of_user: str, 
    ):
        new_pending_user = PendingUser(type_of_user, user_id)

        if new_pending_user is None:
            return None
        
        converted_user = jsonable_encoder(new_pending_user)

        updated_calendar = await CalendarDataHelper.add_one_user_to_calendar(
            request, 
            calendar['_id'], 
            converted_user
        )

        if updated_calendar is None:
            return None
        else:
            return updated_calendar
        

    @staticmethod
    def verify_user_is_in_calendar(
        updated_calendar: Calendar,
        permission_type: str,
        user_id: str
    ):
        pending_users = updated_calendar.get('pending_users', [])
        for pending_user in pending_users:
            if pending_user['_id'] == user_id and pending_user['type'] == permission_type:
                return True
        return False
    

    @staticmethod
    def group_all_user_ids_in_calendar(calendar, user_id):
        all_user_ids = [user_id]

        all_user_ids.extend(calendar['authorized_users'])
        all_user_ids.extend(calendar['view_only_users'])

        for pending_user in calendar['pending_users']:
            all_user_ids.append(pending_user['_id'])

        return all_user_ids


    @staticmethod
    async def remove_calendar_from_users(
        request: Request, 
        all_user_ids: list[str], 
        calendar_id: str
    ):
        errors = 0

        async for user in request.app.db['users'].find({'_id': {'$in': all_user_ids}}):
            try:
                if calendar_id in user['calendars']:
                    await request.app.db['users'].update_one(
                        {'_id': user['_id']}, 
                        {'$pull': {'calendars': calendar_id}}
                    )
            except Exception as e:
                logging.error(f"Error updating calendars for user {user['_id']}: {e}")
                errors += 1
                continue

            try:
                if calendar_id in user['pending_calendars']:
                    await request.app.db['users'].update_one(
                        {'_id': user['_id']}, 
                        {'$pull': {'pending_calendars': calendar_id}}
                    )
            except Exception as e:
                logging.error(f"Error updating pending_calendars for user {user['_id']}: {e}")
                errors += 1
                continue
            
        return errors
    

    @staticmethod
    async def delete_one_calendar(request: Request, calendar_id: str):
        return await request.app.db['calendars'].delete_one({'_id': calendar_id})
    

    @staticmethod
    def log_user_removal_status(users_remove_status: int):
        if users_remove_status > 0:
            return logger.warning(f'When attempting to remove calendar from user instances, {users_remove_status}\'s were not removed')
        

    @staticmethod
    def log_event_removal_status(events_remove_status: int):
        if events_remove_status > 0:
            return logger.warning(f'When attempting to remove events from a calendar, {events_remove_status} events were not removed')


    @staticmethod
    def log_note_removal_status(notes_remove_status: int):
        if notes_remove_status > 0:
            return logger.warning(f'When attempting to remove notes from a calendar, {notes_remove_status} notes were not removed')


    @staticmethod
    async def verify_user_has_calendar_authorization(
        request: Request, 
        user_email: str, 
        calendar_id: str
    ):
        try:
            user = await CalendarDataHelper.find_one_user_by_email(
                request, 
                user_email
            )

            calendar = await CalendarDataHelper.find_one_calendar(
                request,
                calendar_id,
                projection={'authorized_users': 1}
            )

            if user is None or calendar is None:
                return JSONResponse(content={
                    'detail': 'Failed to verify user or calendar being accessed'}, status_code=404
                )

            if user['_id'] in calendar['authorized_users']:
                return True
            else:
                return False
            
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)


    @staticmethod
    async def create_calendar_note(request: Request, user, calendar_id: str):
        try:
            calendar_note_object = await json_parser(request=request)

            if isinstance(calendar_note_object, JSONResponse):
                return calendar_note_object

            created_by_user = user.copy()
            del created_by_user['personal_calendar']

            user_ref = UserRef(
                first_name=created_by_user['first_name'],
                last_name=created_by_user['last_name'],
                user_id=created_by_user['_id'],
            )

            calendar_note = CalendarNote(
                calendar_id=calendar_id,
                note=calendar_note_object['note'],
                type=calendar_note_object['noteType'],
                user_ref=user_ref,
                start_date=datetime.fromisoformat(calendar_note_object['dates']['startDate']),
                end_date=datetime.fromisoformat(calendar_note_object['dates']['endDate']),
            )

            if calendar_note is None:
                return JSONResponse(content={
                    'detail': 'The note you posted is not compatible'}, status_code=404
                )

            upload_note = await CalendarDataHelper.create_calendar_note(request, calendar_note)

            if upload_note is None:
                return JSONResponse(content={
                    'detail': 'Failed to upload new note'}, status_code=422
                )
            
            retrieved_note = await CalendarDataHelper.find_calendar_note(
                request, 
                upload_note.inserted_id
            )

            if retrieved_note is None:
                return JSONResponse(content={
                    'detail': 'Failed to retrieve uploaded note'}
                )
            
            return retrieved_note
        
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def add_note_to_calendar(
        request: Request,
        calendar_id: str,
        note_id: str,
    ):
        try:
            updated_calendar = await CalendarDataHelper.add_calendar_note_to_calendar(
                request,
                calendar_id,
                note_id
            )

            if updated_calendar is None:
                return JSONResponse(content={
                    'detail': 'We could not update that calendar with your note'}, status_code=404
                )
            
            return updated_calendar
        
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def handle_remove_user_from_calendar(
        request: Request,
        user_id: str, 
        calendar_id: str,
        authorized_users: list[str], 
        view_only_users: list[str],
    ):
        removal_status = None

        if user_id in authorized_users:
            removal_status = await CalendarDataHelper.remove_user_from_calendar(
                request,
                user_id,
                calendar_id,
                'authorized_users',
            )

        if user_id in view_only_users:
            removal_status = await CalendarDataHelper.remove_user_from_calendar(
                request,
                user_id,
                calendar_id,
                'view_only_users',
            )

        return removal_status
    

    @staticmethod
    async def create_updated_note(
        request: Request, 
        note: CalendarNote, 
        calendar_id: str
    ):
        try:
            calendar_note_object = await json_parser(request=request)

            if isinstance(calendar_note_object, JSONResponse):
                return calendar_note_object

            user_ref = UserRef(
                first_name=note['created_by']['first_name'],
                last_name=note['created_by']['last_name'],
                user_id=note['created_by']['user_id'],
            )

            calendar_note = CalendarNote(
                calendar_id=calendar_id,
                note=calendar_note_object['note'],
                type=calendar_note_object['noteType'],
                user_ref=user_ref,
                start_date=datetime.fromisoformat(calendar_note_object['dates']['startDate']),
                end_date=datetime.fromisoformat(calendar_note_object['dates']['endDate']),
                id=note['_id'],
            )

            if calendar_note is None:
                return JSONResponse(content={'detail': 'The note you posted is not compatible'}, status_code=404)
            
            return calendar_note
        
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def remove_note_from_previous_calendar(
        request: Request,
        note: CalendarNote,
    ):
        try:
            remove_note_from_calendar = await request.app.db['calendars'].update_one(
                {'_id': note['calendar_id']},
                {'$pull': {'calendar_notes': note['_id']}}
            )

            if remove_note_from_calendar is None:
                return JSONResponse(content={
                    'detail': 'We failed to remove the note from that calendar'}, status_code=422
                )
            
            else:
                return
            
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)
        

    @staticmethod
    async def handle_move_calendar_note_to_new_calendar(
        request: Request,
        note: CalendarNote,
        calendar_id: str,
        note_id: str,
    ):
        try:
            removal_status = await CalendarDataHelper.remove_note_from_previous_calendar(
                request,
                note,
                calendar_id,
            )

            if isinstance(removal_status, JSONResponse):
                return removal_status
            
            add_status = await CalendarDataHelper.add_note_to_calendar(
                request,
                calendar_id,
                note_id,
            )

            if isinstance(add_status, JSONResponse):
                return add_status
            
        except Exception as e:
            return CalendarDataHelper.handle_server_error(e)

        
class UserProjection:
    user_projection = {
        'first_name': 1,
        'last_name': 1,
        'email': 1,
        'job_title': 1,
        'company': 1,
    }