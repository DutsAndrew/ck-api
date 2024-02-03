from fastapi import Request
from fastapi.responses import JSONResponse
from models.team import Team
from models.team import UserRef
from models.calendar import Calendar, PendingUser
from models.project import Project
from models.note import Note
from models.notification import Notification
from controllers.calendar_controller import populate_one_calendar
from fastapi.encoders import jsonable_encoder
from scripts.json_parser import json_parser
import logging
import asyncio

logger = logging.getLogger(__name__)


def order_teams(ordered_team_id_list: list[str], retrieved_teams: list[Team]):
    # ordered_team_id_list must be the un-populated id list of user['teams']
    return sorted(retrieved_teams, key=lambda team: ordered_team_id_list.index(team['_id']))


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
        creator_user_id=new_team.users[0],
    )

    if isinstance(calendar, JSONResponse):
        return calendar
    
    new_team.add_team_calendar(calendar_id=str(calendar.id))

    uploaded_and_populated_team = await upload_team_and_team_calendar_to_db(request, new_team, calendar)

    if isinstance(uploaded_and_populated_team, JSONResponse):
        return uploaded_and_populated_team

    return JSONResponse(content={
        'detail': 'Success! We uploaded your team, invited users, and added a team calendar!',
        'team': jsonable_encoder(uploaded_and_populated_team),
    }, status_code=200)



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
            users=[team_creator['user_id']],
        )

        return new_team
    except Exception as e:
        logger.error(msg=f"error: {e}")
        return JSONResponse(content={'detail': f"failed to create team instance, error: {e}"}, status_code=422)


def build_team_member_objects(team_members: []):
    member_array = []

    for member in team_members:
        try:
            member_array.append(member['user']['_id'])
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
            user_id=pending_user,
        )
        converted_pending_users.append(converted_user)

    return converted_pending_users


async def upload_team_and_team_calendar_to_db(request: Request, new_team: Team, calendar: Calendar):
    try:
        upload_calendar = await request.app.db['calendars'].insert_one(jsonable_encoder(calendar))

        if upload_calendar is None:
            return JSONResponse(content={'detail': 'failed to upload calendar'}, status_code=422)
        
        invite_calendar_users = await invite_users_to_team_calendar(request=request, calendar=calendar)

        if isinstance(invite_calendar_users, JSONResponse):
            return invite_calendar_users
                
        upload_team = await request.app.db['teams'].insert_one(jsonable_encoder(new_team))

        if upload_team is None:
            return JSONResponse(content={'detail': 'failed to upload team'}, status_code=422)
        
        invite_team_users = await invite_users_to_team(request, new_team)

        if isinstance(invite_team_users, JSONResponse):
            return invite_team_users
        
        fetched_team = await request.app.db['teams'].find_one({'_id': upload_team.inserted_id})

        if fetched_team is None:
            return JSONResponse(content={'detail': 'failed to retrieve created team'}, status_code=404)
        
        populated_team = await populate_team(request=request, team=fetched_team)

        return populated_team
        
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={'detail': f'failed to upload calendar and or team to db, error: {e}'}, status_code=422)


async def invite_users_to_team_calendar(request: Request, calendar: Calendar):
    users_to_invite: list[str] = []

    for user in calendar.pending_users:
        users_to_invite.append(user.user_id)

    try:
        # add calendar as a pending one for each invited user
        async for user in request.app.db['users'].find({'_id': {'$in': users_to_invite}}):
            request.app.db['users'].update_one(
                {'_id': user['_id']},
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
    try:
        # add team_id to pending teams array for every invited user
        async for user in request.app.db['users'].find({'_id': {'$in': new_team.pending_users}}):
            request.app.db['users'].update_one(
                {'_id': user['_id']},
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
    

async def get_user_team_data(request: Request, user_email: str):
    # fetch all team refs attached to user
    try:
        user = await request.app.db['users'].find_one(
            {'email': user_email},
            projection={
                'teams': 1,
                'pending_teams': 1,
            }
        )

        if user is None:
            return JSONResponse(content={'detail': 'there was an issue accessing your account'}, status_code=404)
    
        # keep teams in order, as order matters on client
        retrieved_teams = await request.app.db['teams'].find(
            {'_id': {'$in': user['teams']}}
        ).to_list(None)

        retrieved_pending_teams = await request.app.db['teams'].find(
            {'_id': {'$in': user['pending_teams']}}
        ).to_list(None)

        if retrieved_teams is None or retrieved_pending_teams is None:
            return JSONResponse(content={'detail': 'failed to retrieve team data'}, status_code=404)

        # populate each team fully
        populated_teams = await populate_teams(request, retrieved_teams)
        populated_pending_teams = await populate_teams(request, retrieved_pending_teams)

        ordered_teams = order_teams(ordered_team_id_list=user['teams'], retrieved_teams=retrieved_teams)

        if isinstance(populated_teams, JSONResponse):
            return populate_team
        if isinstance(populated_pending_teams, JSONResponse):
            return populated_pending_teams
        
        return JSONResponse(content={
            'detail': 'Success! We populated all of your team data',
            'teams': jsonable_encoder(ordered_teams),
            'pending_teams': jsonable_encoder(populated_pending_teams),
        }, status_code=200)
    
    except Exception as e:
        logger.error(msg=f"{e}")
        return JSONResponse(content={'detail': 'we failed to retrieve your team data'}, status_code=422)


async def populate_teams(request: Request, teams: list[Team]):
    return await asyncio.gather(*[populate_team(request=request, team=team) for team in teams])
    

async def populate_team(request, team: Team): 
    user_projection = {
        'first_name': 1,
        'last_name': 1,
        'email': 1,
        'job_title': 1,
        'company': 1,
        '_id': 1,
    }

    try:
        calendar = await request.app.db['calendars'].find_one({'_id': team['calendar']})
        populated_calendar = await populate_one_calendar(request=request, calendar_id=team['calendar'])
        team['calendar'] = populated_calendar if populated_calendar is not None else calendar
    except Exception as e:
        logger.error(f"Failed to retrieve calendar: {e}")

    try:
        retrieved_users = await request.app.db['users'].find(
            {'_id': {'$in': team['users']}}, 
            projection=user_projection
        ).to_list(None)
        team['users'] = retrieved_users
    except Exception as e:
        logger.error(f"Failed to retrieve users: {e}")

    try:
        retrieved_pending_users = await request.app.db['users'].find(
            {'_id': {'$in': team['pending_users']}},
            projection=user_projection
        ).to_list(None)
        team['pending_users'] = retrieved_pending_users
    except Exception as e:
        logger.error(f"Failed to retrieve pending users: {e}")

    try:
        retrieved_projects = await request.app.db['projects'].find(
            {'_id': {'$in': team['projects']}}
        ).to_list(None)
        team['projects'] = retrieved_projects
    except Exception as e:
        logger.error(f"Failed to retrieve projects: {e}")

    try:
        retrieved_notes = await request.app.db['notes'].find(
            {'_id': {'$in': team['notes']}}
        ).to_list(None)
        team['notes'] = retrieved_notes
    except Exception as e:
        logger.error(f"Failed to retrieve notes: {e}")

    try:
        retrieved_notifications = await request.app.db['notifications'].find(
            {'_id': {'$in': team['notifications']}}
        ).to_list(None)
        team['notifications'] = retrieved_notifications
    except Exception as e:
        logger.error(f"Failed to retrieve notifications: {e}")

    return team


async def reorder_teams_list(request: Request, user_email: str):
    try:
        user = await request.app.db['users'].find_one(
            {'email': user_email},
            projection={
                'teams': 1,
                'id': 1,
            }
        )

        if user is None:
            return JSONResponse(content={'detail': 'there was an issue accessing your account'}, status_code=404)
        
        body = await json_parser(request=request)

        if sorted(user['teams']) != sorted(body):
            return JSONResponse(content={'detail': 'team lists were not the same'}, status_code=422)
        
        update_user = await update_user_team_list_order(request, body, user['_id'])

        if isinstance(update_user, JSONResponse):
            return update_user

        # keep teams in order, as order matters on client
        retrieved_teams = await request.app.db['teams'].find(
            {'_id': {'$in': user['teams']}}
        ).to_list(None)

        populated_teams = await populate_teams(request=request, teams=retrieved_teams)
        ordered_teams = order_teams(ordered_team_id_list=user['teams'], retrieved_teams=retrieved_teams)

        if isinstance(populated_teams, JSONResponse):
            return populated_teams
                
        return JSONResponse(content={
            'detail': 'Success! We reordered your teams!',
            'teams': jsonable_encoder(ordered_teams),
        }, status_code=200)

  
    except Exception as e:
        logger.error(f'{e}')
        return JSONResponse(content={'detail': 'failed to access server to reorder list'}, status_code=422)
    

async def update_user_team_list_order(request: Request, updated_list: list[str], user_id: str):
    updated_user = await request.app.db['users'].update_one(
        {'_id': user_id},
        {'$set': {'teams': updated_list}}
    )

    if updated_user is None:
        return JSONResponse(content={'detail': 'we failed to updated the users team list'}, status_code=422)

    return updated_user