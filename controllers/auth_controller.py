from models.user import User
from fastapi import Request
from fastapi.encoders import jsonable_encoder
import bcrypt

async def sign_up(request: Request, user: User):
    # form has been validated with the User model, each user object passed in should have the following:
    # email, first_name, last_name, request.body.get('password'), and 2 optional fields: job_title and company

    # check if email has already been registered
    try:
        user_lookup = await request.app.database['users'].find_one(
            {"email": user.email}
        )
        if user_lookup is not None:
            return {
                "message": "That email is already registered with us, please login to your account or create one with a new email",
                "email": user.email,
                "company": user.company,
                "first_name": user.first_name,
                "job_title": user.job_title,
                "last_name": user.last_name,
                "password": user.password,
                "confirm_password": user.password,
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
                upload_user = await request.app.database["users"].insert_one(user_data)
                if upload_user:
                    return {
                        "message": "Success, we created your account",
                        "success": True,
                    }
                else:
                    return {
                        "message": "Failed to save user",
                        "email": user.email,
                        "company": user.company,
                        "first_name": user.first_name,
                        "job_title": user.job_title,
                        "last_name": user.last_name,
                        "password": request.body.get('password'),
                        "confirm_password": request.body.get('confirm_password'),
                    }  
            # failed to upload to db, abort, send form data back
            except Exception as e:
                return {
                    "message": "We failed to create your account, please resubmit your form",
                        "email": user.email,
                        "company": user.company,
                        "first_name": user.first_name,
                        "job_title": user.job_title,
                        "last_name": user.last_name,
                        "password": request.body.get('password'),
                        "confirm_password": request.body.get('confirm_password'),
                }
            
    except Exception as e:
        return {
            "message": f"We could not confirm that email address and had to abort, the error was: {e}"
        }