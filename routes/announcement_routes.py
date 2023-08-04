from fastapi import APIRouter
from controllers import announcements_controller

announcement_router = APIRouter()

# all announcement routes go here
@announcement_router.get('/')
async def get_welcome():
    return {
        "Not Implemented"
    }