from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from models.team import Team
from models.team import UserRef
from models.calendar import Calendar
from models.color_scheme import ColorScheme
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from scripts.json_parser import json_parser
import logging

logger = logging.getLogger(__name__)


async def create_team(request: Request):
    request_body = await json_parser(request=request)
    
    new_team = create_team_object(request_body)

    if isinstance(new_team, JSONResponse):
        return new_team

    print(new_team)



def create_team_object(request_body: object):
    team_creator = request_body['teamCreator']
    team_name = request_body['teamName']
    team_description = request_body['teamDescription']
    team_color = request_body['teamColor']
    team_members = request_body['teamMembers']

    converted_team_members = build_team_member_objects(team_members)

    try:
        new_team = Team(
            description=team_description,
            name=team_name,
            notifications=[],
            tasks=[],
            team_color=team_color,
            team_lead="",
            pending_users=converted_team_members,
            users=[
                UserRef(
                    first_name=team_creator['first_name'],
                    last_name=team_creator['last_name'],
                    job_title=team_creator['job_title'],
                    company=team_creator['company'],
                    user_id=team_creator['user_id'],
                ),
            ],
        )

        return new_team
    except Exception as e:
        logger.error(msg=f"error: {e}")
        return JSONResponse(content={'detail': f"failed to create team instance, error: {e}"}, status_code=422)


def build_team_member_objects(team_members):
    member_array = []

    for member in team_members:
        try:
            user = UserRef(
                first_name=member['first_name'],
                last_name=member['last_name'],
                job_title=member['job_title'],
                company=member['company'],
                user_id=member['_id'],
            )
            member_array.append(user)
        except Exception as e:
            continue
        
    return member_array