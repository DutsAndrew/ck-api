from models.user import UserLogin
from datetime import datetime, timedelta
from scripts.jwt_helper_functions import get_jwt_env_variables
import jwt
import uuid

def encode_bearer_token(user_login: UserLogin):
    jwt_config = get_jwt_env_variables()

    # get timestamp value for jwt.encode()
    exp_time = datetime.utcnow() + timedelta(hours=12)
    exp_timestamp = exp_time.timestamp()

    # generate bearer token
    bearer_payload = {
        "email": user_login.email,
        "sub": str(uuid.uuid4()),
        "exp": (datetime.utcnow() + timedelta(hours=12)).timestamp(),
        "issued_at": datetime.utcnow().timestamp(),
    }

    bearer_token = jwt.encode(
        bearer_payload,
        jwt_config["JWT_SECRET"],
        algorithm=jwt_config["JWT_ALGORITHM"],
    )

    return bearer_token
    

def encode_refresh_token(user_id):
    jwt_config = get_jwt_env_variables()

    # generate refresh token
    refresh_payload = {
        "sub": user_id,
        "exp": (datetime.utcnow() + timedelta(days=30)).timestamp(),
        "issued_at": datetime.utcnow().timestamp(),
    }

    refresh_token = jwt.encode(
        refresh_payload,
        jwt_config["JWT_SECRET"],
        algorithm=jwt_config["JWT_ALGORITHM"],
    )

    return refresh_token

