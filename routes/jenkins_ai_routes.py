from fastapi import APIRouter
from controllers import jenkins_ai_controller

jenkins_ai_router = APIRouter()

# all jenkins_ai routes go here
@jenkins_ai_router.get('/')
async def get_welcome():
    return {
        "Not Implemented"
    }