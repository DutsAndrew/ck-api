from fastapi import APIRouter
from controllers import messaging_controller

messaging_router = APIRouter()

# all messaging routes go here
@messaging_router.get('/')
async def get_welcome():
    return {
        "Not Implemented"
    }