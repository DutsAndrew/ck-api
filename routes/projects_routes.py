from fastapi import APIRouter, Request, Depends
from scripts.jwt_token_decoders import process_bearer_token
from controllers import projects_controller

projects_router = APIRouter()

@projects_router.post('/createProject')
async def post_team(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await projects_controller.create_project(request=request)