from fastapi import APIRouter, Request, Depends
from scripts.jwt_token_decoders import process_bearer_token
from controllers import teams_controller

teams_router = APIRouter()

# all team routes go here
@teams_router.get('/')
async def get_welcome():
    return {
        "Not Implemented"
    }


@teams_router.post('/createTeam')
async def post_team(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await teams_controller.create_team(request=request)


@teams_router.get('/getUserTeams')
async def get_user_teams(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await teams_controller.get_user_team_data(request, token['email'])