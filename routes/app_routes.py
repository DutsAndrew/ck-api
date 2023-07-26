from fastapi import APIRouter
from controllers import app_controller

app_router = APIRouter()

# all app routes go here
@app_router.get('/')
async def get_welcome():
    return await app_controller.welcome_request()