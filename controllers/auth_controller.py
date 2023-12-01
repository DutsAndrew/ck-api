from models.user import User, UserLogin
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from scripts.jwt_token_encoders import encode_bearer_token, encode_refresh_token
from models.calendar import Calendar
import bcrypt

async def sign_up(request: Request, user: User):
    # check if email has already been registered
    try:
        user_lookup = await request.app.db['users'].find_one(
            {"email": user.email}
        )
        if user_lookup is not None:
            return JSONResponse(content={'detail': 'Email already registered'}, status_code=400)
        else:
            # no errors on form, email is not already registered and has been checked, continue sanitizing
            # hash password
            password_in_bytes = user.password.encode("utf-8")
            salt = bcrypt.gensalt()
            hash = bcrypt.hashpw(password_in_bytes, salt)

            # store hashed password
            user.password = hash

            # build personal calendar
            calendar = await build_personal_calendar_for_new_user(request, user)

            if isinstance(calendar, JSONResponse):
                return calendar
            
            # assign calendar id to user
            user.personal_calendar = calendar

            print(user)

            # convert user object into a dictionary
            user_data = jsonable_encoder(user)

            upload_user = await request.app.db["users"].insert_one(user_data)

            if upload_user is None:
                return JSONResponse(content={'detail': 'Failed to save user'}, status_code=500)   
            
            user_data_stripped = {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "job_title": user.job_title if hasattr(user, 'job_title') else None,
                "company": user.company if hasattr(user, 'company') else None,
            }
            return {
                "message": "Success, we created your account",
                "success": True,
                "user": user_data_stripped,
            }
    except Exception as e:
        return JSONResponse(content={'detail': f'Server side error, which was: {e}'}, status_code=500)
    

async def build_personal_calendar_for_new_user(request: Request, user: User):
    new_calendar = Calendar(calendar_type="personal", name=f"{user.first_name}'s Personal Calendar", user_id=user.id)
    print(new_calendar)
    calendar_upload = await request.app.db['calendars'].insert_one(jsonable_encoder(new_calendar))
    print(calendar_upload)
    if calendar_upload is not None:
        return new_calendar.id
    else:
        return JSONResponse(content={'detail': 'Failed to create personal calendar'}, status_code=422)
    
    
async def user_login(request: Request, user_login: UserLogin):
    try:
        user_lookup = await request.app.db['users'].find_one({
            "email": user_login.email,
        })

        if user_lookup is None or not bcrypt.checkpw(
            user_login.password.encode(), 
            user_lookup['password'].encode()
        ):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # prepare user instance to send back
        user_response = user_lookup.copy()
        del user_response['password']
        
        bearer_token = encode_bearer_token(user_login)
        refresh_token = encode_refresh_token(user_lookup['_id'])

        response = JSONResponse({
            "message": "You have been successfully logged in",
            "status": True,
            "user": user_response,
        })

        response.headers["Authorization"] = f"Bearer {bearer_token}"
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax")

        return response


    except Exception as e:
        return {
            "detail": "There was a server error processing your request",
            "errors": e,
        }