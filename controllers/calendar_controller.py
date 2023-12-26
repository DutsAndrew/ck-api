from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from models.calendar import PendingUser, Calendar, CalendarNote, Event, UserRef
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from datetime import datetime
from scripts.json_parser import json_parser
import logging

logger = logging.getLogger(__name__)

async def fetch_calendar_app_data(request: Request):
    try:
        calendar_data_lookup = await request.app.db['app-data'].find_one(
            {"app_data_type": "calendar"}
        )

        if calendar_data_lookup is not None:
            
            converted_data = dict(calendar_data_lookup)
            if "_id" in converted_data:
                converted_data["_id"] = str(converted_data["_id"])

            return JSONResponse(
                content={
                    'detail': 'Calendar Data Loaded',
                    'data': converted_data,
                },
                status_code=200
            )
        else:
            raise HTTPException(
                status_code=404,
                detail='Calendar data not found',
            )
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JSONResponse(
            content={
                'detail': 'There was an issue processing your request',
            },
            status_code=500
        )
    

async def fetch_all_user_calendar_data(request: Request, user_email: str):
    try:
        user = await request.app.db['users'].find_one(
            {"email": user_email},
            projection={
                'calendars': 1,
                'pending_calendars': 1,
                'personal_calendar': 1,
            },
        )

        if not user:
            return JSONResponse(content={'detail': 'The account you are using does not exist'}, status_code=404)
               
        populated_calendars = await populate_all_team_calendars(request, user)
        user['calendars'] = populated_calendars['calendars']
        user['pending_calendars'] = populated_calendars['pending_calendars']
        personal_calendar = await populate_one_calendar(request, calendar_id=user['personal_calendar'])
        
        if personal_calendar is None:
            return JSONResponse(content={'detail': 'personal calendar could not be populated'}, status_code=422)
        
        user['personal_calendar'] = personal_calendar

        return JSONResponse(
            content={
                'detail': 'All possible calendars fetched',
                'updated_user': user,
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JSONResponse(
            content={
                'detail': 'There was an issue processing your request',
            },
            status_code=500
        )
    

async def populate_all_team_calendars(request, user):
    calendar_ids = [str(calendar_id) for calendar_id in user['calendars']]
    pending_calendar_ids = [str(calendar_id) for calendar_id in user['pending_calendars']]
    
    calendars = await populate_individual_calendars(request, calendar_ids)
    pending_calendars = await populate_individual_calendars(request, pending_calendar_ids)

    return {
        'calendars': calendars,
        'pending_calendars': pending_calendars,
    }


async def populate_individual_calendars(request: Request, calendar_ids: list[str]):
    if len(calendar_ids) == 0: return []

    calendars = []

    authorized_user_ids = set()
    pending_user_ids = set()
    view_only_user_ids = set()
    calendar_notes_ids = set()
    event_ids = set()

    # POPULATE ALL CALENDARS AND STORE ALL DB REFS
    async for calendar in request.app.db['calendars'].find({
        '_id': {'$in': calendar_ids}
    }):
        calendars.append(calendar)
        authorized_user_ids.update(calendar.get('authorized_users', []))
        view_only_user_ids.update(calendar.get('view_only_users', []))
        calendar_notes_ids.update(calendar.get('calendar_notes', []))
        event_ids.update(calendar.get('events', []))

        for pending_user in calendar.get('pending_users', []):
            user_id = pending_user.get('_id')
            if user_id:
                pending_user_ids.add(user_id)

    user_projection = {
        'first_name': 1,
        'last_name': 1,
        'email': 1,
        'job_title': 1,
        'company': 1,
    }

    # POPULATE ALL USER INSTANCES USING THE USER REFS
    authorized_users = await request.app.db['users'].find({
        '_id': {'$in': list(authorized_user_ids)}},
        projection=user_projection
    ).to_list(None)
    view_only_users = await request.app.db['users'].find({
        '_id': {'$in': list(view_only_user_ids)}},
        projection=user_projection
    ).to_list(None)
    calendar_notes = await request.app.db['calendar_notes'].find({
        '_id': {'$in': list(calendar_notes_ids)}},
    ).to_list(None)
    events = await request.app.db['events'].find({
        '_id': {'$in': list(event_ids)},
    }).to_list(None)

    # CREATE DICT WITH USER REF TIED TO USER INSTANCE
    calendar_authorized_users_dict = {str(user['_id']): user for user in authorized_users}
    calendar_view_only_users_dict = {str(user['_id']): user for user in view_only_users}

    # LOOP THROUGH CALENDARS TO STORE USER INSTANCES IN EACH CALENDAR
    for calendar in calendars:
        authorized_user_ids = calendar.get('authorized_users', [])
        view_only_user_ids = calendar.get('view_only_users', [])
        pending_user_ids = [str(pending_user.get('_id')) for pending_user in calendar.get('pending_users', [])]

        # WAIT TO FIND ALL PENDING USERS FOR EACH CALENDAR INDIVIDUALLY TO MAINTAIN DATA STRUCTURE NEEDED
        pending_users = await request.app.db['users'].find({
            '_id': {'$in': pending_user_ids}},
            projection=user_projection
        ).to_list(None)

        # MERGE POPULATED PENDING USER INSTANCE WITH THE ORIGINAL PENDING OBJECT TYPE
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

        # STORE ALL USERS TO THEIR RESPECTIVE CALENDAR
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


async def fetch_users_query(request: Request):
    try: 
        user_query = request.query_params.get('user', default=None)
        
        if user_query:
            # cursor for querying the db
            cursor = request.app.db['users'].find(
                {"$text": {"$search": user_query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})])

            # store non-sensitive data of users and async loop cursor through db
            user_search_results = []
            async for document in cursor:
                user_ref = {
                    "company": document["company"] if document["company"] else '',
                    "email": document["email"] if document["email"] else '',
                    "first_name": document["first_name"] if document["first_name"] else '',
                    "job_title": document["job_title"] if document["job_title"] else '',
                    "last_name": document["last_name"] if document["last_name"] else '',
                    "_id": document["_id"] if document["_id"] else '',
                }
                user_search_results.append({"user": user_ref, "score": document.pop("score")})


            if user_search_results is not None:
                # convert the user results to dict
                return JSONResponse(
                    content={
                        'detail': 'Results found',
                        'user_results': user_search_results,
                    },
                    status_code=200
                )

            else:
                return JSONResponse(
                    content={
                        'detail': 'There were no matches for that query',
                    },
                    status_code=404
                )

        else:
            return JSONResponse(
                content={
                    'detail': 'No userQuery parameter to lookup in db',
                },
                status_code=422
            )

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JSONResponse(
            content={
                'detail': 'There was an issue processing your request'
            },
            status_code=500
        )
    

async def post_new_calendar(request: Request):
    request_body = await json_parser(request=request)

    if isinstance(request_body, JSONResponse):
        return request_body

    calendar_color = request_body['calendarColor']
    calendar_name = request_body['calendarName']
    user_id = request_body['createdBy']
    authorized_users = request_body['authorizedUsers']
    view_only_users = request_body['viewOnlyUsers']
    # if needed each user has email, first_name, last_name, job_title, and company listed

    pending_users = compile_pending_users(authorized_users, view_only_users)

    new_calendar = Calendar(
        calendar_color=calendar_color,
        calendar_type='team',
        name=calendar_name,
        user_id=user_id,
        pending_users=pending_users
    )

    return await upload_new_calendar(request, new_calendar, pending_users, user_id)


def compile_pending_users(authorized_users, view_only_users):
    pending_users = []

    # loop through and make all users in each list a pending user object for creating the calendar object
    for user in authorized_users:
        pending_user = PendingUser('authorized', user['user']['_id'])
        pending_users.append(pending_user)

    for user in view_only_users:
        pending_user = PendingUser('view_only', user['user']['_id'])
        pending_users.append(pending_user)

    return pending_users

    
async def upload_new_calendar(request: Request, new_calendar: Calendar, pending_users, user_id: str):
    try:
        calendar_data = jsonable_encoder(new_calendar)
        calendar_upload = await request.app.db['calendars'].insert_one(calendar_data)
        calendar_id = str(calendar_upload.inserted_id)
        uploaded_calendar = await request.app.db['calendars'].find_one({'_id': calendar_id})
        updated_user_who_created_calendar = await request.app.db['users'].update_one(
            {'_id': str(user_id)}, {'$push': {'calendars': calendar_id}})

        if calendar_upload is None or uploaded_calendar is None or updated_user_who_created_calendar is None:
            return JSONResponse(
                content={'detail': 'Failed to save, retrieve, and update calendar to user'},
                status_code=500
            )

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

        if unsuccessful_users_updated > 0:
            return JSONResponse(
                content={
                    'detail': 'Calendar created, all users were not invited successfully, you may want to remove and re-invite users in the Calendar Editor to ensure all users are invited correctly',
                    'calendar': uploaded_calendar,
                },
                status_code=200
            )
        
        if successful_users_updated == len(pending_users) or (successful_users_updated == 0 and unsuccessful_users_updated == 0):
            populated_calendar = await populate_one_calendar(request, calendar_id)
            if populated_calendar is None:
                return JSONResponse(content={'detail': 'Calendar was not able to be populated'}, status_code=422)
            
            return JSONResponse(
                content={
                    'detail': 'Calendar created and all necessary users added',
                    'calendar': populated_calendar,
                },
                status_code=200
            )
        
        return JSONResponse(content={'detail': 'Something went wrong'})

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JSONResponse(
            content={'detail': 'There was an issue processing your request'},
            status_code=500
        )

    
async def remove_user_from_calendar(request: Request, calendar_id: str, user_type: str, user_id: str, user_making_request_email: str):
    try:
        # query user and calendar to perform operations
        user, calendar = await validate_user_and_calendar(request, user_making_request_email, calendar_id)

        if user is None or calendar is None:
            return JSONResponse(content={'detail': 'Invalid request'}, status_code=404)
                
        if user_id == calendar['created_by']:
            return JSONResponse(content={'detail': 'The creator of the calendar can never be removed'}, status_code=422)
        
        # if user making request isn't authorized return immediately
        if not has_calendar_permissions(user, calendar):
            return JSONResponse(content={'detail': 'insufficient permissions'})
        
        # remove user that was requested to be removed
        filtered_calendar = filter_out_user_from_calendar_list(user_id, calendar, user_type)

        # just a validity check to ensure that an API call wasn't made with a false type, return if that's the case
        if filtered_calendar is None:
            return JSONResponse(content={'detail': 'Failed to update calendar'}, status_code=422)

        # update calendar with new filtered calendar
        update_calendar = await request.app.db['calendars'].replace_one({'_id': calendar_id}, filtered_calendar)

        if update_calendar is None:
            return JSONResponse(content={'detail': 'Failed to update calendar to remove user'}, status_code=422)
        
        # find updated calendar and populate all users on it before returning
        updated_and_repopulated_calendar = await populate_one_calendar(request, calendar_id)

        if updated_and_repopulated_calendar is None:
            return JSONResponse(content={'detail': 'Failed to refetch updated calendar with removed user'}, status_code=404)
        
        return JSONResponse(
            content={
                'detail': 'User successfully removed from calendar',
                'updated_calendar': updated_and_repopulated_calendar,
            },
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JSONResponse(
            content={'detail': 'There was an issue processing your request'},
            status_code=500
        )
    

async def validate_user_and_calendar(request, user_email, calendar_id):
    user = await request.app.db['users'].find_one({'email': user_email})
    calendar = await request.app.db['calendars'].find_one({'_id': calendar_id})
    return user, calendar


def has_calendar_permissions(user, calendar):
    return user is not None and (calendar['created_by'] == user['_id'] or user['_id'] in calendar['authorized_users'])
    

def filter_out_user_from_calendar_list(user_id, calendar, user_type):
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


async def populate_one_calendar(request: Request, calendar_id: str):
    
    calendar = None
    
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
    user_projection = {
        'first_name': 1,
        'last_name': 1,
        'email': 1,
        'job_title': 1,
        'company': 1,
    }

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


async def add_user_to_calendar(
        request: Request, 
        calendar_id: str, 
        user_id: str, 
        permission_type: str, 
        email_of_user_making_change: str
    ):
      try:
          user_making_request, calendar = await validate_user_and_calendar(request, email_of_user_making_change, calendar_id)
          if user_making_request is None or calendar is None:
              return JSONResponse(content={'detail': 'There was an issue processing the user and calendar sent'}, status_code=404)
                    
          user_to_add = await request.app.db['users'].find_one({'_id': user_id}, projection={})

          if user_to_add is None:
              return JSONResponse(content={'detail': 'The user to add cannot be found'}, status_code=404)
          
          if not has_calendar_permissions(user_making_request, calendar):
              return JSONResponse(content={'detail': 'The user making that request is not authorized'}, status_code=422)
                    
          updated_array = await append_new_user_to_calendar_user_list(
              request,
              user_id, 
              calendar, 
              permission_type, 
          )

          if updated_array is None:
              return JSONResponse(content={'detail': 'There was an issue adding that user, either the user was already in the list, or we failed to update the list'}, status_code=422) 
          
          updated_calendar = await request.app.db['calendars'].find_one({'_id': calendar['_id']})

          if not verify_user_was_added_to_calendar(updated_calendar, permission_type, user_id):
              return JSONResponse(content={'detail': 'User was not added to calendar successfully'}, status_code=422)
                    
          populated_calendar = await populate_one_calendar(request, updated_calendar['_id'])
          
          return JSONResponse(content={
              'detail': 'We successfully added user to your calendar',
              'updated_calendar': populated_calendar,
          }, status_code=200)
      
      except Exception as e:
          logger.error(f"Error processing request: {e}")
          return JSONResponse(
              content={'detail': 'There was an issue processing your request'},
              status_code=500
          )


# NEED TO SETUP SO THAT ALL USERS ARE STORED AS PENDING USERS
async def append_new_user_to_calendar_user_list(
        request: Request, 
        user_id: str, 
        calendar: Calendar, 
        type_of_user: str, 
    ):
        new_pending_user = PendingUser(type_of_user, user_id)
        if new_pending_user is None:
            return None
        converted_user = jsonable_encoder(new_pending_user)
        updated_calendar = await request.app.db['calendars'].update_one(
            {'_id': calendar['_id']},
            {'$push': {'pending_users': converted_user}}
        )

        if updated_calendar is None:
            return None
        else:
            return updated_calendar
        

def verify_user_was_added_to_calendar(
        updated_calendar: Calendar,
        permission_type,
        user_id: str
    ):
        pending_users = updated_calendar.get('pending_users', [])
        for pending_user in pending_users:
            if pending_user['_id'] == user_id and pending_user['type'] == permission_type:
                return True
        return False
        

async def delete_calendar(request: Request, calendar_id: str, user_id: str):
    try:
        user = await request.app.db['users'].find_one({'_id': user_id})
        calendar = await request.app.db['calendars'].find_one({'_id': calendar_id})

        if user is None or calendar is None:
            return JSONResponse(content={'detail': 'Invalid data requested'}, status_code=404)

        if calendar['created_by'] != user['_id']:
            return JSONResponse(content={'detail': 'You cannot delete this calendar as you are not it\'s creator'}, status_code=422)

        all_user_ids = compile_all_user_ids_from_calendar(calendar, user['_id'])
        await remove_calendar_id_from_all_users(request, all_user_ids, calendar['_id'])
        calendar_delete = await request.app.db['calendars'].delete_one({'_id': calendar['_id']})

        if calendar_delete is None:
            return JSONResponse(content={'detail': 'There were issues deleting that calendar'}, status_code=422)

        return JSONResponse(content={'detail': 'Calendar deleted', 'calendar_id': calendar['_id']}, status_code=200)
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JSONResponse(content={'detail': 'There was an issue processing your request'}, status_code=500)


def compile_all_user_ids_from_calendar(calendar, user_id):
    all_user_ids = [user_id]

    all_user_ids.extend(calendar['authorized_users'])
    all_user_ids.extend(calendar['view_only_users'])

    for pending_user in calendar['pending_users']:
        all_user_ids.append(pending_user['_id'])

    return all_user_ids


async def remove_calendar_id_from_all_users(request: Request, all_user_ids: list[str], calendar_id: str):
    async for user in request.app.db['users'].find({'_id': {'$in': all_user_ids}}):
        if calendar_id in user['calendars']:
            await request.app.db['users'].update_one(
                {'_id': user['_id']}, 
                {'$pull': {'calendars': calendar_id}}
            )
        if calendar_id in user['pending_calendars']:
            await request.app.db['users'].update_one(
                {'_id': user['_id']}, 
                {'$pull': {'pending_calendars': calendar_id}}
            )


async def user_leave_calendar_request(request, calendar_id, user_id):
    try:
        calendar = await request.app.db['calendars'].find_one({'_id': calendar_id})
        user = await request.app.db['users'].find_one({'_id': user_id})

        if calendar is None or user is None:
            return JSONResponse(content={'detail': 'The user or calendar sent do not exist'}, status_code=404)

        if calendar['created_by'] == user['_id']:
            return JSONResponse(content={'detail': 'You cannot leave a calendar you have created'})

        updated_user = await request.app.db['users'].update_one(
            {'_id': user['_id']},
            {'$pull': {'calendars': calendar['_id']}}
        )

        updated_calendar = None
        if user['_id'] in calendar['authorized_users']:
            updated_calendar = await request.app.db['calendars'].update_one(
                {'_id': calendar['_id']},
                {'$pull': {'authorized_users': user['_id']}}
            )
        if user['_id'] in calendar['view_only_users']:
            updated_calendar = await request.app.db['calendars'].update_one(
                {'_id': calendar['_id']},
                {'$pull': {'view_only_users': user['_id']}}
            )

        if updated_calendar is None or updated_user is None:
            return JSONResponse(content={'detail': 'Failed to remove user from calendar'}, status_code=422)
        
        return JSONResponse(content={
            'detail': 'Successfully removed user',
            'calendar_id_to_remove': calendar['_id']
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JSONResponse(content={'detail': 'There was an issue processing your request'}, status_code=500)
    

async def post_note(request: Request, calendar_id: str, user_making_request: str):
    permissions = await verify_user_has_calendar_authorization(request, user_making_request, calendar_id)
    if permissions is False or isinstance(permissions, JSONResponse):
        return JSONResponse(content={'detail': 'We could not validate permissions'}, status_code=404)
        
    user = await request.app.db['users'].find_one(
        {'email': user_making_request}, 
        projection={
            'first_name': 1,
            'last_name': 1,
            'personal_calendar': 1
        },
    )

    calendar_note = await create_calendar_note_and_verify(request, user, calendar_id)

    if isinstance(calendar_note, JSONResponse):
        return calendar_note

    calendar = await request.app.db['calendars'].find_one({'_id': calendar_id})

    if calendar is None or user is None:
        return JSONResponse(content={'detail': 'the user or calendar you\'re working on is invalid'}, status_code=404)
        
    # Send calendar_note in with data to add it to the correct calendar
    update_calendar_with_note = await add_note_to_calendar(
        request,
        calendar,
        calendar_note['_id'],
    )

    if isinstance(update_calendar_with_note, JSONResponse):
        return update_calendar_with_note
    
    # Fetch calendar to get the updated version
    updated_calendar_with_note = await retrieve_updated_calendar_with_new_note(
        request,
        calendar_id,
    )

    if isinstance(updated_calendar_with_note, JSONResponse):
        return updated_calendar_with_note
        
    return JSONResponse(content={
        'detail': 'Successfully updated calendar with note',
        'updated_calendar': updated_calendar_with_note,
    }, status_code=200)
    

async def verify_user_has_calendar_authorization(request: Request, user_email: str, calendar_id: str):
    try:
        user = await request.app.db['users'].find_one(
            {'email': user_email},
            projection={'_id': 1}
        )

        calendar = await request.app.db['calendars'].find_one(
            {'_id': calendar_id},
            projection={'authorized_users': 1}
        )

        if user is None or calendar is None:
            return JSONResponse(content={'detail': 'Failed to verify user or calendar being accessed'}, status_code=404)

        if user['_id'] in calendar['authorized_users']:
            return True
        else:
            return False
        
    except Exception as e:
        logger.error(f"Calendar note could not be created: {e}")
        return JSONResponse(content={'detail': 'There was an error creating that calendar note'}, status_code=422)
    

async def create_calendar_note_and_verify(request: Request, user, calendar_id: str):
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
            return JSONResponse(content={'detail': 'The note you posted is not compatible'}, status_code=404)

        upload_note = await request.app.db['calendar_notes'].insert_one(jsonable_encoder(calendar_note))

        if upload_note is None:
            return JSONResponse(content={'detail': 'Failed to upload new note'}, status_code=422)
        
        retrieved_note = await request.app.db['calendar_notes'].find_one({'_id': upload_note.inserted_id})

        if retrieved_note is None:
            return JSONResponse(content={'detail': 'Failed to retrieve uploaded note'})
        
        return retrieved_note
    
    except (ValueError, TypeError, ValidationError) as e:
        logger.error(f"Calendar note could not be created: {e}")
        return JSONResponse(content={'detail': 'There was an error creating that calendar note'}, status_code=422)
    

async def add_note_to_calendar(
        request: Request,
        calendar: Calendar,
        calendar_note_id: str,
    ):
        try:
            updated_calendar = await request.app.db['calendars'].update_one(
                {'_id': calendar['_id']},
                {'$push': {'calendar_notes': calendar_note_id}}
            )

            if updated_calendar is None:
                return JSONResponse(content={'detail': 'We could not update that calendar with your note'}, status_code=404)
            
            return updated_calendar
        
        except Exception as e:
            logger.error(f"Could not add note to calendar: {e}")
            return JSONResponse(content={'detail': 'There was an error adding your note to that calendar'}, status_code=422)


async def retrieve_updated_calendar_with_new_note(request: Request, calendar_id: str):
    calendar_with_updated_note = await populate_one_calendar(request, calendar_id)

    if calendar_with_updated_note is None:
        return JSONResponse(content={'detail': 'Failed to retrieve updated calendar with note'}, status_code=422)
    
    return calendar_with_updated_note
    

async def update_note(request: Request, calendar_id: str, note_id: str, user_making_request_email: str):
    permissions = await verify_user_has_calendar_authorization(request, user_making_request_email, calendar_id)
    if permissions is False or isinstance(permissions, JSONResponse):
        return JSONResponse(content={'detail': 'We could not validate permissions'}, status_code=404)

    note = await request.app.db['calendar_notes'].find_one({'_id': note_id})
    
    if note is None:
        return JSONResponse(content={'detail': 'That note could not be found'})
    
    updated_note = await create_updated_note(
        request, 
        note, 
        calendar_id, 
    )

    if isinstance(updated_note, JSONResponse):
        return updated_note

    if updated_note is None:
      return JSONResponse(content={'detail': 'We were unable to create an updated version of that note'}, status_code=422)
        
    remove_note_from_calendar = await remove_note_from_previous_calendar(
        request,
        note,
        calendar_id,
    )

    if isinstance(remove_note_from_calendar, JSONResponse):
        return remove_note_from_calendar
    
    add_note_to_calendar = await add_note_to_calendar_on_update(
        request,
        calendar_id,
        note['_id'],
    )

    if isinstance(add_note_to_calendar, JSONResponse):
        return add_note_to_calendar
            
    upload_updated_note = await request.app.db['calendar_notes'].update_one(
        {'_id': note_id},
        {'$set': jsonable_encoder(updated_note)}
    )

    if upload_updated_note is None:
        return JSONResponse(content={'detail': 'We were unable to update the previous note version'}, status_code=404)
    
    return JSONResponse(content={
        'detail': 'Successfully updated the note',
        'updated_note': jsonable_encoder(updated_note),
    }, status_code=200)


async def create_updated_note(request: Request, note: CalendarNote, calendar_id: str):
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
    
    except (ValueError, TypeError, ValidationError) as e:
        logger.error(f"Calendar note could not be updated: {e}")
        return JSONResponse(content={'detail': 'There was an error updating that calendar note'}, status_code=422)
    

async def remove_note_from_previous_calendar(
        request: Request,
        note: CalendarNote,
        calendar_id: str,
    ):
        try:
            if note['calendar_id'] is not calendar_id:
                remove_note_from_calendar = await request.app.db['calendars'].update_one(
                    {'_id': note['calendar_id']},
                    {'$pull': {'calendar_notes': note['_id']}}
                )
                if remove_note_from_calendar is None:
                    return JSONResponse(content={'detail': 'We failed to remove the note from that calendar'}, status_code=422)
                else:
                    return
            else:
                return
            
        except Exception as e:
            logger.error(f"Calendar note could not be removed from the requested calendar: {e}")
            return JSONResponse(content={'detail': 'There was an error removing the note from it\'s previous calendar'}, status_code=422)
        

async def add_note_to_calendar_on_update(
        request: Request, 
        calendar_id: str, 
        note_id: str, 
    ):
        try:
            calendar_to_update = await request.app.db['calendars'].update_one(
                {'_id': calendar_id},
                {'$push': {'calendar_notes': note_id}}
            )
            if calendar_to_update is None:
                return JSONResponse(content={'detail': 'We failed to update the new calendar with the note'}, status_code=422)
            else:
                return
            
        except Exception as e:
            logger.error(f"Calendar note could not be added to the requested calendar: {e}")
            return JSONResponse(content={'detail': 'There was an error adding the note to it\'s new calendar'}, status_code=422)
        

async def delete_note(request: Request, calendar_id: str, calendar_note_id: str):
    calendar, note = await fetch_calendar_and_note(request, calendar_id, calendar_note_id)

    if isinstance(calendar, JSONResponse) or isinstance(note, JSONResponse):
        return calendar or note
    
    note_removal_status = await remove_calendar_note_from_db(request, calendar_id, calendar_note_id)

    if isinstance(note_removal_status, JSONResponse):
        return note_removal_status
    
    return JSONResponse(content={'detail': 'Success! Calendar was updated, note was removed'},status_code=200)


async def fetch_calendar_and_note(request: Request, calendar_id: str, calendar_note_id: str):
    calendar = await request.app.db['calendars'].find_one({'_id': calendar_id}, projection={})
    note = await request.app.db['calendar_notes'].find_one({'_id': calendar_note_id}, projection={})

    if calendar is None or note is None:
        return JSONResponse(content={'detail': 'failed to retrieve calendar or calendar note'}, status_code=404)
    
    return calendar, note


async def remove_calendar_note_from_db(request: Request, calendar_id: str, calendar_note_id: str):
    remove_calendar_note_ref = await request.app.db['calendars'].update_one(
        {'_id': calendar_id},
        {'$pull': {'calendar_notes': calendar_note_id}}
    )

    if remove_calendar_note_ref is None:
        return JSONResponse(content={'detail': 'could not remove calendar note from calendar'}, status_code=422)

    remove_calendar_note = await request.app.db['calendar_notes'].delete_one({'_id': calendar_note_id})

    if remove_calendar_note is None:
        return JSONResponse(content={'detail': 'we failed to remove that calendar note'}, status_code=422)
    
    return remove_calendar_note


async def post_event(request: Request, calendar_id: str, user_making_request_email):
    user_ref = await build_user_reference(request, user_making_request_email)

    if isinstance(user_ref, JSONResponse):
        return user_ref
    
    request_body = await json_parser(request=request)

    if isinstance(request_body, JSONResponse):
        return request_body
    
    new_event = create_event_instance(request_body, calendar_id, user_ref)

    uploaded_event = await upload_new_event(request, calendar_id, new_event)

    if isinstance(uploaded_event, JSONResponse):
        return uploaded_event
    
    updated_calendar = await populate_one_calendar(request, calendar_id)

    if updated_calendar is None:
        return JSONResponse(content={'detail': 'failed to retrieve populated calendar'}, status_code=422)
    
    return JSONResponse(content={
        'detail': 'Success! We uploaded your event',
        'updated_calendar': updated_calendar,
    }, status_code=200)


async def build_user_reference(request: Request, user_making_request_email: str):
    user_ref = await request.app.db['users'].find_one(
        {'email': user_making_request_email},
        projection={
            "first_name": 1,
            "last_name": 1,
        }
    )

    if user_ref is None:
        return JSONResponse(content={'detail': 'the user making the request is not valid'}, status_code=422)
    
    return user_ref


def create_event_instance(request_body: dict, calendar_id: str, user_ref: UserRef):
    compiled_user_ref = UserRef(
        first_name=user_ref['first_name'],
        last_name=user_ref['last_name'],
        user_id=user_ref['_id'],
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
    )

    if new_calendar is None:
        return JSONResponse(content={'detail': 'we could not create your calendar event'}, status_code=422)

    return new_calendar


async def upload_new_event(request, calendar_id, new_event):
    upload_event = await request.app.db['events'].insert_one(jsonable_encoder(new_event))

    if upload_event is None:
        return JSONResponse(content={'detail': 'failed to upload event'}, status_code=422)

    update_calendar = await request.app.db['calendars'].update_one(
        {'_id': calendar_id},
        {'$push': {'events': str(new_event.id)}}
    )

    if update_calendar is None:
        return JSONResponse(content={'detail': 'failed to update calendar with new event'}, status_code=422)
    
    posted_event = await request.app.db['events'].find_one({'_id': str(new_event.id)})

    if posted_event is None:
        return JSONResponse(content={'detail': 'we could not retrieve the posted event'}, status_code=422)
    
    return posted_event


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
        
        updated_calendar = await populate_one_calendar(request, calendar_id)

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

    updated_calendar = await populate_one_calendar(request, calendar_id)

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

        current_user_permissions = get_user_permissions_in_calendar(calendar, user_id)

        if current_user_permissions is None:
            return JSONResponse(content={'detail': 'that user does not belong to this calendar'}, status_code=422)
        
        current_user_permissions = await change_user_calendar_permissions(
            request, 
            calendar_id,
            current_user_permissions,
            new_user_permissions,
            user_id
        )


def get_user_permissions_in_calendar(calendar: Calendar, userId: str):
    if userId in calendar.authorized_users:
        return 'authorized'
    
    if userId in calendar.view_only_users:
        return 'view_only'

    for userInstance in calendar.pending_users:
        if userId == userInstance._id:
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
        
        


async def remove_user_permissions(
        request: Request, 
        calendar_id: str, 
        current_user_permissions: str, 
        user_id: str,
    ):
        if current_user_permissions is 'pending':
            pending_users = await request.app.db['calendars'].find_one(
                {'_id': calendar_id},
                projection={
                    'pending_users': 1,
                }
            )

            if pending_users is None:
                return JSONResponse(content={'detail': 'could not retrieve pending users'}, status_code=422)

            for user in pending_users.pending_users:
                if user._id is user_id:
                    pass

        calendar = await request.app.db['calendars'].update_one(
            {'_id': calendar_id},
            {'$pull': {f"{current_user_permissions}_users": user_id}}
        )

        if calendar is None:
            return JSONResponse(content={'detail': 'that user\'s permission could not be changed'}, status_code=422)

        return calendar


