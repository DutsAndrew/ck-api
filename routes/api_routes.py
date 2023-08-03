from fastapi import APIRouter, Request, Body
from controllers import account_controller, announcements_controller
from controllers import app_controller, auth_controller
from controllers import calendar_controller, jenkins_ai_controller
from controllers import messaging_controller, notes_controller, pages_controller
from controllers import tasks_controller, teams_controller

from models.user import User, UserLogin

api_router = APIRouter()

# all /api prefixed routes will go here
@api_router.get('/')
async def get_api():
    return await app_controller.api_welcome_request()


@api_router.post('/signup')
async def post_signup(request: Request, user: User):
    return await auth_controller.sign_up(request, user)

@api_router.post('/login')
async def post_login(request: Request, user_login: UserLogin):
    return await auth_controller.user_login(request, user_login)