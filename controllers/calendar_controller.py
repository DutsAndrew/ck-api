from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from models.calendar import PendingUser, Calendar
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
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
    

async def fetch_all_user_calendar_data(request: Request, userEmail: str):
    try:
        user = await request.app.db['users'].find_one(
            {"email": userEmail},
            projection={
                'calendars': 1,
                'pending_calendars': 1,
            },
        )
        if not user:
            return JSONResponse(
                content={
                    'detail': 'The account you are using does not exist'
                },
                status_code=404
            )
        else:
            populated_calendars = await populate_all_calendars(request, user)
            user['calendars'] = populated_calendars['calendars']
            user['pending_calendars'] = populated_calendars['pending_calendars']

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
    

async def populate_all_calendars(request, user):
    calendar_ids = [str(calendar_id) for calendar_id in user['calendars']]
    pending_calendar_ids = [str(calendar_id) for calendar_id in user['pending_calendars']]
    
    calendars = await populate_individual_calendars(request, calendar_ids)
    pending_calendars = await populate_individual_calendars(request, pending_calendar_ids)

    return {
        'calendars': calendars,
        'pending_calendars': pending_calendars,
    }


async def populate_individual_calendars(request: Request, calendar_ids: list[str]):
    calendars = []
    authorized_user_ids = set()
    pending_user_ids = set()
    view_only_user_ids = set()

    # POPULATE ALL CALENDARS AND STORE ALL USER REFS
    async for calendar in request.app.db['calendars'].find({
        '_id': {'$in': calendar_ids}
    }):
        calendars.append(calendar)
        authorized_user_ids.update(calendar.get('authorized_users', []))
        view_only_user_ids.update(calendar.get('view_only_users', []))

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
    request_body = await request.json()
    calendar_name = request_body['calendarName']
    user_id = request_body['createdBy']
    authorized_users = request_body['authorizedUsers']
    view_only_users = request_body['viewOnlyUsers']
    # if needed each user has email, first_name, last_name, job_title, and company listed

    pending_users = compile_pending_users(authorized_users, view_only_users)

    new_calendar = Calendar(
        'team',
        calendar_name,
        user_id,
        pending_users
    )

    return await upload_new_calendar(request, new_calendar, pending_users)


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

    
async def upload_new_calendar(request: Request, new_calendar, pending_users):
    try:
        calendar_data = jsonable_encoder(new_calendar)
        calendar_upload = await request.app.db['calendars'].insert_one(calendar_data)
        calendar_id = str(calendar_upload.inserted_id)
        calendar_to_return = await request.app.db['calendars'].find_one({
            "_id": calendar_id
        })
        if calendar_upload and calendar_to_return:
            # loop through each user to add the calendar ref into their user instance for pending invites
            successful_users_updated = 0
            unsuccessful_users_updated = 0
            for user in pending_users:
                update_user = await request.app.db['users'].find_one_and_update(
                    {"_id": user.user_id},
                    {"$push": {"pending_calendars": calendar_id}},
                )
                if update_user:
                    successful_users_updated += 1
                else:
                    unsuccessful_users_updated += 1
            if unsuccessful_users_updated > 0:
                return JSONResponse(
                    content={
                        'detail': 'Calendar created, all users were not invited successfully, you may want to remove and re-invite users in the Calendar Editor to ensure all users are invited correctly',
                        'calendar': calendar_to_return,
                    },
                    status_code=200
                )
            if successful_users_updated == len(pending_users):
                return JSONResponse(
                        content={
                            'detail': 'Calendar created and all necessary users added',
                            'calendar': calendar_to_return,
                        },
                        status_code=200
                    )
            else:
                return JSONResponse(
                    content={
                        'detail': 'Calendar created and all necessary users added, calendar not retrieved',
                    }
                )      
        else:
            return JSONResponse(
                content={
                    'detail': 'Failed to save calendar',
                },
                status_code=500
            )
    except Exception as e:
                logger.error(f"Error processing request: {e}")
                return JSONResponse(
                    content={
                        'detail': 'There was an issue processing your request'
                    },
                    status_code=500
                )
    
async def remove_user_from_calendar(request: Request, calendar_id: str, type: str, user_making_request_email: str):
    user_to_remove_id = request.query_params.get('user')

    try:
        user, calendar = await validate_user_and_calendar(request, user_making_request_email, calendar_id)

        if user is None or calendar is None:
            return JSONResponse(content={'detail': 'Invalid request'}, status_code=404)

        if not has_calendar_permissions(user, calendar):
            return JSONResponse(content={'detail': 'insufficient permissions'})

        filtered_calendar = filter_out_user_from_calendar_list(user_to_remove_id, calendar, type)

        if filtered_calendar is None:
            return JSONResponse(content={'detail': 'Failed to update calendar'}, status_code=422)

        update_calendar = await request.app.db['calendars'].replace_one({'_id': calendar_id}, filtered_calendar)

        if update_calendar is None:
            return JSONResponse(content={'detail': 'Failed to update calendar to remove user'}, status_code=422)
        
        updated_calendar = await request.app.db['calendars'].find_one( # RE-CONFIGURE TO POPULATE ALL CALENDAR FIELDS BEFORE RETURNING
            {'_id': calendar_id}
        )

        if updated_calendar is None:
            return JSONResponse(content={'detail': 'Failed to refetch updated calendar with removed user'}, status_code=404)
        
        return JSONResponse(
            content={
                'detail': 'User successfully removed from calendar',
                'updated_calendar': updated_calendar,
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
    

def filter_out_user_from_calendar_list(user_to_remove_id, calendar, type):
    if type == 'authorized':
        if calendar['created_by'] == user_to_remove_id: # prevent users from removing creator of calendar
            return None
        calendar['authorized_users'].remove(user_to_remove_id)
    elif type == 'pending':
        updated_pending_users = [user for user in calendar['pending_users'] if user['_id'] != user_to_remove_id] # users are nested in pending list, need to loop through to modify
        calendar['pending_users'] = updated_pending_users
    elif type == 'view-only':
        calendar['view_only_users'].remove(user_to_remove_id)
    else:
        return None # invalid type
    
    return calendar