from fastapi import APIRouter, Request, Depends
from controllers import account_controller
from scripts.jwt_token_decoders import process_bearer_token

account_router = APIRouter()

# all account routes go here
@account_router.get('/')
async def get_welcome():
    return {
        "Not Implemented"
    }

@account_router.post('/delete')
async def post_delete(request: Request, user: bool = Depends(process_bearer_token)):
    return account_controller.delete_account(request)