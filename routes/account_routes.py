from fastapi import APIRouter, Request, Depends
from controllers import account_controller
from scripts.jwt_token_decoders import process_bearer_token

account_router = APIRouter()

# all account routes go here
@account_router.get('/')
async def get_welcome():
    return {
        "use the /account route to perform various account CRUD operations"
    }

@account_router.post('/delete')
async def post_delete(request: Request, token: str | bool = Depends(process_bearer_token)):
    return await account_controller.delete_account(request, token)