from datetime import datetime
from models.user import User
from fastapi import Request
import bcrypt

async def sign_up(request: Request, user: User):
    # form has been validated with the User model, each user object passed in should have the following:
    # email, first_name, last_name, request.body.get('password'), and 2 optional fields: job_title and company

    # check if email has already been registered
    check_if_email_exists = await request.app.database['users'].find_one(
            {"email": user.email}
    )
    return {
        "results": check_if_email_exists,
        "email": user.email,
    }
    # try:
        
    #     if check_if_email_exists is not None:
    #         return {
    #             "message": "That email is already registered with us, please login to your account or create one with a new email",
    #             "email": user.email,
    #             "company": user.company,
    #             "first_name": user.first_name,
    #             "job_title": user.job_title,
    #             "last_name": user.last_name,
    #             "password": request.body.get('password'),
    #             "confirm_password": request.body.get('confirm_password'),
    #         }      
    #     else:
    #         # no errors on form, email is not already registered and has been checked, continue sanitizing
    #         hashed_password = bcrypt.hashpw(request.body.get('password').encode("utf-8"), bcrypt.gensalt())

    #         # create an instance of user model
    #         new_user = User(**user.model_dict(), password=hashed_password)

    #         # begin uploading user to db
    #         try: 
    #             upload_user = await request.app.database["users"].insert_one(new_user)
    #             if upload_user:
    #                 return {
    #                     "message": "Success, we created your account",
    #                     "success": True,
    #                 }
    #             else:
    #                 return {
    #                     "message": "Failed to save user",
    #                     "email": user.email,
    #                     "company": user.company,
    #                     "first_name": user.first_name,
    #                     "job_title": user.job_title,
    #                     "last_name": user.last_name,
    #                     "password": request.body.get('password'),
    #                     "confirm_password": request.body.get('confirm_password'),
    #                 }
                
    #         # failed to upload to db, abort, send form data back
    #         except Exception as e:
    #             return {
    #                 "message": "We failed to create your account, please resubmit your form",
    #                     "email": user.email,
    #                     "company": user.company,
    #                     "first_name": user.first_name,
    #                     "job_title": user.job_title,
    #                     "last_name": user.last_name,
    #                     "password": request.body.get('password'),
    #                     "confirm_password": request.body.get('confirm_password'),
    #             }
    
    # except Exception as e:
    #     return {
    #         "message": f"We could not confirm that email address and had to abort, the error was: {e}"
    #     }