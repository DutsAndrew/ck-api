import jwt
from scripts.jwt_helper_functions import get_jwt_env_variables
from fastapi import HTTPException, Header, Request
from scripts.ttl_cache import token_cache


async def process_bearer_token(request: Request, authorization: str = Header(...)):
    try:
        bearer_token = authorization.split(" ")[1] # extract token from bearer string
        return await validate_bearer_token(request, bearer_token)
    except IndexError:
        HTTPException(status_code=401, detail="Invalid Bearer token")


async def validate_bearer_token(request, bearer_token):
    if bearer_token in token_cache:
        return token_cache[bearer_token]
    
    decoded_token = await decode_bearer_token(bearer_token)
    verified_token = await verify_bearer_token(request, decoded_token)

    if not verified_token:
        return HTTPException(status_code=401, detail="Invalid Bearer token")
    else:
        # add to cache, user is verified
        token_cache[bearer_token] = decoded_token
        return decoded_token


def decode_bearer_token(bearer_token):
    try:
        jwt_config = get_jwt_env_variables()
        payload = jwt.decode(
            bearer_token,
            jwt_config['JWT_SECRET'],
            algorithms=jwt_config["JWT_ALGORITHM"]
        )
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Bearer token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid Bearer token")
    

async def verify_bearer_token(request, decoded_token):
    verify_token = await request.app.db['users'].find_one({
            "email": decoded_token.get("email")
        })
    
    return verify_token is not None