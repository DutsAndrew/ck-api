from fastapi import APIRouter, Request, Depends
from controllers import calendar_controller
from scripts.jwt_token_decoders import process_bearer_token

calendar_router = APIRouter()

# all calendar routes go here
@calendar_router.get('/')
async def get_calendar_data(request: Request, token: str | bool = Depends(process_bearer_token)):
    print(request, token)
    return await calendar_controller.fetch_calendar_app_data(request)