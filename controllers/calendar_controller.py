from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from models.calendar import PendingUser, Calendar
from fastapi.encoders import jsonable_encoder
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

    await upload_new_calendar(request, new_calendar, pending_users)


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