from fastapi import APIRouter
from controllers import pages_controller

pages_router = APIRouter()

# all page routes go here
@pages_router.get('/')
async def get_welcome():
    return {
        "Not Implemented"
    }