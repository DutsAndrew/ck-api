from fastapi import APIRouter
from controllers import account_controller, announcements_controller
from controllers import app_controller, auth_controller
from controllers import calendar_controller, jenkins_ai_controller
from controllers import messaging_controller, notes_controller, pages_controller
from controllers import tasks_controller, teams_controller

api_router = APIRouter()

# all /api prefixed routes will go here
@api_router.get('/api/', tags=['api'])
async def get_api():
    return await app_controller.api_welcome_request()


@api_router.post('/api/signup', tags=['api'])
async def post_signup():
    return await auth_controller.sign_up()