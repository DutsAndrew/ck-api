from fastapi import APIRouter, Request, Depends
from controllers import calendar_controller
from scripts.jwt_token_decoders import process_bearer_token

calendar_router = APIRouter()

@calendar_router.get('/')
async def get_calendar_data(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.fetch_calendar_app_data(request)

@calendar_router.get('/getUserCalendarData')
async def get_user_calendar_data(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.fetch_all_user_calendar_data(request, token.get('email'))

@calendar_router.get('/userQuery')
async def get_user_query(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.fetch_users_query(request)

@calendar_router.post('/uploadCalendar')
async def post_calendar_upload(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.post_new_calendar(request)

@calendar_router.delete('/{id}/removeUserFromCalendar/{type}')
async def delete_user(id: str, type: str, request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.remove_user_from_calendar(request, id, type, token['email'])

@calendar_router.post('/{calendar_id}/addUser/{user_id}/{type_of_user}/{type_of_pending_user}')
async def post_new_user(
        calendar_id: str,
        user_id: str, 
        type_of_user: str,
        type_of_pending_user: str,
        request: Request, 
        token: str | bool = Depends(process_bearer_token)
    ):
        return await calendar_controller.add_user_to_calendar(
             request, 
             calendar_id, 
             user_id, 
             type_of_user, 
             type_of_pending_user, 
             token['email']
        )

@calendar_router.delete('/{calendar_id}/deleteCalendar/{user_id}')
async def delete_calendar(request: Request, calendar_id: str, user_id: str, token: str | bool = Depends(process_bearer_token)):
     return await calendar_controller.delete_calendar(request, calendar_id, user_id)