from fastapi import APIRouter
from controllers import notes_controller

notes_router = APIRouter()

# all note routes go here
@notes_router.get('/')
async def get_welcome():
    return {
        "Not Implemented"
    }