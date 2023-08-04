from fastapi import APIRouter
from controllers import tasks_controller

tasks_router = APIRouter()

# all task routes go here
@tasks_router.get('/')
async def get_welcome():
    return {
        "Not Implemented"
    }