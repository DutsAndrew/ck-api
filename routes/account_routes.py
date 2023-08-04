from fastapi import APIRouter
from controllers import account_controller

account_router = APIRouter()

# all account routes go here
@account_router.get('/')
async def get_welcome():
    return {
        "Not Implemented"
    }