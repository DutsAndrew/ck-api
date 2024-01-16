from fastapi import APIRouter, Request, Depends
from controllers import users_controller
from scripts.jwt_token_decoders import process_bearer_token

users_router = APIRouter()


@users_router.get('/userQuery')
async def get_user_query(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await users_controller.fetch_users_query(request)