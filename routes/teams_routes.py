from fastapi import APIRouter
from controllers import teams_controller

teams_router = APIRouter()

# all team routes go here
@teams_router.get('/')
async def get_welcome():
    return {
        "Not Implemented"
    }