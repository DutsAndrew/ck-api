from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

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