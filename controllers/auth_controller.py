from models.user import User, UserLogin
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from scripts.jwt_token_encoders import encode_bearer_token, encode_refresh_token
import bcrypt

async def sign_up(request: Request, user: User):
    
    # create user instance without sensitive data to send back to user
    user_data_stripped = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "job_title": user.job_title if hasattr(user, 'job_title') else None,
        "company": user.company if hasattr(user, 'company') else None,
    }

    # check if email has already been registered
    try:
        user_lookup = await request.app.db['users'].find_one(
            {"email": user.email}
        )
        if user_lookup is not None:
            return {
                "message": "That email is already registered with us, please login to your account or create one with a new email",
                "user": user_data_stripped,
            }      
        else:
            # no errors on form, email is not already registered and has been checked, continue sanitizing

            # hash password
            password_in_bytes = user.password.encode("utf-8")
            salt = bcrypt.gensalt()
            hash = bcrypt.hashpw(password_in_bytes, salt)

            # overwrite user's password with the hashed version
            user.password = hash

            # convert user object into a dictionary
            user_data = jsonable_encoder(user)

            # begin uploading user to db
            try: 
                upload_user = await request.app.db["users"].insert_one(user_data)
                if upload_user:
                    return {
                        "message": "Success, we created your account",
                        "success": True,
                        "user": user_data_stripped,
                    }
                else:
                    return {
                        "message": "Failed to save user",
                        "user": user_data_stripped,
                    }  
            # failed to upload to db, abort, send form data back
            except Exception as e:
                return {
                    "message": "We failed to create your account, please resubmit your form",
                    "user": user_data_stripped,
                }
            
    except Exception as e:
        return {
            "message": f"There was a server side issue processing this request, the error was: {e}"
        }
    
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
        
        bearer_token = encode_bearer_token(user_login)
        refresh_token = encode_refresh_token(user_lookup['_id'])

        response = JSONResponse({
            "message": "You have been successfully logged in",
            "status": True,
        })
        response.headers["Authorization"] = f"Bearer {bearer_token}"
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax")

        return response


    except Exception as e:
        return {
            "message": "There was a server error processing your request",
            "errors": e,
        }