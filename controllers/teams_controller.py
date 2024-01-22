from fastapi import Request
from fastapi.responses import JSONResponse
from models.team import Team
from models.team import UserRef
from models.calendar import Calendar, PendingUser
from fastapi.encoders import jsonable_encoder
from scripts.json_parser import json_parser
import logging

logger = logging.getLogger(__name__)


async def create_team(request: Request):
    request_body = await json_parser(request=request)
    
    new_team = create_team_object(request_body)

    if isinstance(new_team, JSONResponse):
        return new_team
        
    calendar = create_calendar_object(
        team_id=str(new_team.id), 
        team_color=new_team.team_color,
        team_name=new_team.name,
        pending_users=new_team.pending_users,
        creator_user_id=new_team.users[0].user_id,
    )

    if isinstance(calendar, JSONResponse):
        return calendar
    
    new_team.add_team_calendar(calendar_id=str(calendar.id))

    uploaded_objects = await upload_team_and_team_calendar_to_db(request, new_team, calendar)

    if isinstance(uploaded_objects, JSONResponse):
        return uploaded_objects

    return JSONResponse(content={'detail': 'Success! We uploaded your team, invited users, and added a team calendar!'}, status_code=200)



def create_team_object(request_body: object):
    team_creator = request_body['teamCreator']
    team_name = request_body['teamName']
    team_description = request_body['teamDescription']
    team_color = request_body['teamColor']
    team_members = request_body['teamMembers']

    try:
        converted_team_members = build_team_member_objects(team_members)

        if isinstance(converted_team_members, JSONResponse):
            return converted_team_members

        new_team = Team(
            description=team_description,
            name=team_name,
            team_color=team_color,
            team_lead=None,
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


def build_team_member_objects(team_members: []):
    member_array = []

    for member in team_members:
        try:
            user = UserRef(
                first_name=member['user']['first_name'],
                last_name=member['user']['last_name'],
                job_title=member['user']['job_title'],
                company=member['user']['company'],
                user_id=member['user']['_id'],
            )
            member_array.append(user)
        except Exception as e:
            logger.error(e)
            return JSONResponse(content={'detail': f'we failed to add a user as a team member, error: {e}'}, status_code=422)
                        
    return member_array


def create_calendar_object(
        team_id: str, 
        team_color: str,
        team_name: str,
        pending_users: list,
        creator_user_id: str,
        ):   
    
    try:
        calendar_obj = Calendar(
            calendar_type='team-calendar',
            calendar_color=team_color,
            name=f"{team_name} - Team Calendar",
            user_id=creator_user_id,
            pending_users=convert_user_ref_list_to_pending_calendar_users_list(pending_users),
            team_id=team_id,
        )
        return calendar_obj
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={'detail': f'we failed to create a team calendar for the team, error: {e}'}, status_code=422)



def convert_user_ref_list_to_pending_calendar_users_list(pending_users: list[UserRef]):
    converted_pending_users: list[PendingUser] = []

    for pending_user in pending_users:
        converted_user = PendingUser(
            type='authorized',
            user_id=pending_user.user_id,
        )
        converted_pending_users.append(converted_user)

    return converted_pending_users


async def upload_team_and_team_calendar_to_db(request: Request, new_team: Team, calendar: Calendar):
    try:
        upload_calendar = request.app.db['calendars'].insert_one(jsonable_encoder(calendar))

        if upload_calendar is None:
            return JSONResponse(content={'detail': 'failed to upload calendar'}, status_code=422)
        
        invite_calendar_users = await invite_users_to_team_calendar(request=request, calendar=calendar)

        if isinstance(invite_calendar_users, JSONResponse):
            return invite_calendar_users
                
        upload_team = request.app.db['teams'].insert_one(new_team.encode_team_for_upload())

        if upload_team is None:
            return JSONResponse(content={'detail': 'failed to upload team'}, status_code=422)
        
        invite_team_users = await invite_users_to_team(request, new_team)

        if isinstance(invite_team_users, JSONResponse):
            return invite_team_users

        return {
            upload_calendar,
            upload_team,
        }
        
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={'detail': f'failed to upload calendar and or team to db, error: {e}'}, status_code=422)


async def invite_users_to_team_calendar(request: Request, calendar: Calendar):
    users_to_invite: list[str] = []

    for pending_user in calendar.pending_users:
        users_to_invite.append(pending_user.user_id)

    try:
        # add calendar as a pending one for each invited user
        async for user_id in request.app.db['users'].find({'_id': {'$in': users_to_invite}}):
            request.app.db['users'].update_one(
                {'_id': user_id},
                {'$push': {'pending_calendars': str(calendar.id)}}
            )

        # user who created teh calendar should have it automatically added as an approved calendar
        request.app.db['users'].update_one(
            {'_id': calendar.authorized_users[0]},
            {'$push': {'calendars': str(calendar.id)}}
        )
        return
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={'detail': f'we ran into an issue updating the invited users to the team calendar {e}'}, status_code=422)
    

async def invite_users_to_team(request: Request, new_team: Team):
    users_to_invite: list[str] = []
    merged_user_lists = new_team.users + new_team.pending_users

    for user in merged_user_lists:
        users_to_invite.append(user.user_id)

    try:
        # add team_id to pending teams array for every invited user
        async for user_id in request.app.db['users'].find({'_id': {'$in': users_to_invite}}):
            request.app.db['users'].update_one(
                {'_id': user_id},
                {'$push': {'pending_teams': str(new_team.id)}}
            )

        # add team id to user who created the team automatically
        request.app.db['users'].update_one(
            {'_id': new_team.users[0]},
            {'$push': {'teams': str(new_team.id)}}
        )

    except Exception as e:
        logger.error(e)
        return JSONResponse(content={'detail': 'we failed to invite users to the team, error: {e}'}, status_code=422)