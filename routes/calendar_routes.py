from fastapi import APIRouter, Request, Depends
from controllers import calendar_controller
from scripts.jwt_token_decoders import process_bearer_token

calendar_router = APIRouter()

@calendar_router.get('/')
async def get_calendar_data(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.fetch_calendar_app_data(request)

@calendar_router.get('/userQuery')
async def get_user_query(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.fetch_users_query(request)

@calendar_router.post('/uploadCalendar')
async def post_calendar_upload(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.post_new_calendar(request)