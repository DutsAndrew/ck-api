from fastapi import APIRouter, Request, Depends
from controllers import calendar_controller
from scripts.jwt_token_decoders import process_bearer_token

calendar_router = APIRouter()


@calendar_router.get('/')
async def get_calendar_data(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.fetch_calendar_app_data(request)


@calendar_router.get('/getUserCalendarData')
async def get_user_calendar_data(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.fetch_all_user_calendar_data(request, token.get('email'))


@calendar_router.get('/userQuery')
async def get_user_query(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.fetch_users_query(request)


@calendar_router.post('/uploadCalendar')
async def post_calendar_upload(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.post_new_calendar(request)


@calendar_router.delete('/{calendar_id}/removeUserFromCalendar/{user_type}/{user_id}')
async def delete_user(request: Request, calendar_id: str, user_type: str, user_id: str, token: str | bool = Depends(process_bearer_token)):
    return await calendar_controller.remove_user_from_calendar(request, calendar_id, user_type, user_id, token['email'])


@calendar_router.post('/{calendar_id}/addUser/{user_id}/{permission_type}')
async def post_new_user(
        request: Request, 
        calendar_id: str,
        user_id: str, 
        permission_type: str,
        token: str | bool = Depends(process_bearer_token)
    ):
        return await calendar_controller.add_user_to_calendar(
             request, 
             calendar_id, 
             user_id, 
             permission_type, 
             token['email']
        )


@calendar_router.delete('/{calendar_id}/deleteCalendar/{user_id}')
async def delete_calendar(
        request: Request, 
        calendar_id: str, 
        user_id: str, 
        token: str | bool = Depends(process_bearer_token)
    ):
        return await calendar_controller.delete_calendar(request, calendar_id, user_id)


@calendar_router.post('/{calendar_id}/addNote')
async def post_calendar_note(
        request: Request,
        calendar_id: str,
        token: str | bool = Depends(process_bearer_token)
     ):
        return await calendar_controller.post_note(request, calendar_id, token['email'])


@calendar_router.put('/{calendar_id}/updateNote/{note_id}')
async def update_calendar_note(
        request: Request,
        calendar_id: str,
        note_id: str,
        token: str | bool = Depends(process_bearer_token)
    ):
        return await calendar_controller.update_note(request, calendar_id, note_id, token['email'])


@calendar_router.delete('/{calendar_id}/deleteNote/{calendar_note_id}')
async def delete_calendar_note(
        request: Request, 
        calendar_id: str, 
        calendar_note_id: str, 
        token: str | bool = Depends(process_bearer_token)
    ):
        return await calendar_controller.delete_note(request, calendar_id, calendar_note_id)


@calendar_router.post('/{calendar_id}/createEvent')
async def post_event(
        request: Request, 
        calendar_id: str,
        token: str | bool = Depends(process_bearer_token),
    ):
        return await calendar_controller.post_event(request, calendar_id, token['email'])


@calendar_router.put('/{calendar_id}/editEvent/{event_id}')
async def put_calendar_event(
        request: Request,
        calendar_id: str,
        event_id: str,
        token: str | bool = Depends(process_bearer_token)
    ):
        return await calendar_controller.put_event(request, calendar_id, event_id)


@calendar_router.delete('/{calendar_id}/deleteEvent/{event_id}')
async def delete_calendar_event(
        request: Request,
        calendar_id: str,
        event_id: str,
        token: str | bool = Depends(process_bearer_token)
    ):
        return await calendar_controller.delete_event(request, calendar_id, event_id)


@calendar_router.put('/{calendar_id}/{permission_type}/updateUserPermissions/{userId}')
async def put_calendar_user_permissions(
        request: Request,
        calendar_id: str,
        permission_type: str,
        userId: str,
    ):
        return await calendar_controller.update_user_permissions(
            request,
            calendar_id,
            permission_type,
            userId,
        )