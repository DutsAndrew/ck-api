from models.user import UserLogin
from datetime import datetime
from dotenv import dotenv_values
import uuid
import jwt

def get_env_variables():
    config = dotenv_values('.env')
    jwt_config = {
        "JWT_SECRET": config["JWT_SECRET"],
        "JWT_ALGORITHM": config["JWT_ALGORITHM"]
    }
    return jwt_config

def encode_session_token(user_login: UserLogin):
    jwt_config = get_env_variables()

    # generate session token
    access_payload = {
        "email": user_login.email,
        "sub": uuid.uuid4(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15) # access token is only open for 15 minutes
    }

    access_token = jwt.encode(
        access_payload,
        jwt_config["JWT_SECRET"],
        algorithm=jwt_config["JWT_ALGORITHM"],
    )

    return access_token
    
def encode_refresh_token(user_login: UserLogin, user_id: str):
    jwt_config = get_env_variables()

    # generate refresh token
    refresh_payload = {
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7) # 7 days from now
    }

    refresh_token = jwt.encode(
        refresh_payload,
        jwt_config["JWT_SECRET"],
        algorithm=jwt_config["JWT_ALGORITHM"],
    )

    return refresh_token