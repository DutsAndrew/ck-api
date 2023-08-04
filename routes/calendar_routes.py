from fastapi import APIRouter
from controllers import calendar_controller

calendar_router = APIRouter()

# all calendar routes go here
@calendar_router.get('/')
async def get_welcome():
    return {
        "Not Implemented"
    }