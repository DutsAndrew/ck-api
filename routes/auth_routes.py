from fastapi import APIRouter, Request
from controllers import auth_controller

from models.user import User, UserLogin

auth_router = APIRouter()

@auth_router.post('/signup')
async def post_signup(request: Request, user: User):
    return await auth_controller.sign_up(request, user)

@auth_router.post('/login')
async def post_login(request: Request, user_login: UserLogin):
    return await auth_controller.user_login(request, user_login)