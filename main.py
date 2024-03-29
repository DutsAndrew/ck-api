from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
from motor.motor_asyncio import AsyncIOMotorClient
from scripts.task_runner import task_runner, stop_task_runner
import certifi
import threading

# import routes
from routes.account_routes import account_router
from routes.announcement_routes import announcement_router
from routes.app_routes import app_router
from routes.auth_routes import auth_router
from routes.calendar_routes import calendar_router
from routes.jenkins_ai_routes import jenkins_ai_router
from routes.messaging_routes import messaging_router
from routes.notes_routes import notes_router
from routes.pages_routes import pages_router
from routes.projects_routes import projects_router
from routes.tasks_routes import tasks_router
from routes.teams_routes import teams_router
from routes.users_routes import users_router


# import custom middleware
from scripts.custom_middleware import ErrorLoggingMiddleware


app = FastAPI()
# task_thread = None


# MIDDLEWARE CHAIN
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization"],
)

### DEV FUNCTION TO CHECK ERRORS WITH REQUESTS/RESPONSES IN API
# @app.middleware("http")
# async def log_headers(request: Request, call_next):
#     print("Request Headers:", request.headers)
#     print("Cookies in request:", request.cookies)
#     response = await call_next(request)
#     print("Response Headers:", response.headers)
#     return response


app.add_middleware(ErrorLoggingMiddleware)


async def setup_db_client():
    config = dotenv_values(".env") # get .env files
    app.mongodb_client = AsyncIOMotorClient(config["DEV_MONGO_URI"], tlsCAFile=certifi.where())
    app.db = app.mongodb_client[config["DEV_DB_NAME"]]
    print("Connected to MongoDB!")
    return app # return app instance after setting up db for testing files


async def shutdown_db_client():
    app.mongodb_client.close()


@app.on_event("startup")
async def startup_event():
    await setup_db_client()
    
    # global task_thread

    # task_thread = threading.Thread(target=task_runner, args=(app,))
    # task_thread.start()


@app.on_event("shutdown")
async def shutdown_event():
    # stop_task_runner()
    await shutdown_db_client()

    # global task_thread
    
    # if task_thread and task_thread.is_alive():
    #     task_thread.join(timeout=5)



# link in all routes to app
app.include_router(account_router, tags=["account"], prefix="/account")
app.include_router(announcement_router, tags=["announcement"], prefix="/announcement")
app.include_router(app_router)
app.include_router(auth_router, tags=["auth"], prefix="/auth")
app.include_router(calendar_router, tags=["calendar"], prefix="/calendar")
app.include_router(jenkins_ai_router, tags=["jenkins-ai"], prefix="/jenkins-ai")
app.include_router(messaging_router, tags=["message"], prefix="/message")
app.include_router(notes_router, tags=["note"], prefix="/note")
app.include_router(pages_router, tags=["page"], prefix="/page")
app.include_router(projects_router, tags=["projects"], prefix="/project")
app.include_router(tasks_router, tags=["task"], prefix="/task")
app.include_router(teams_router, tags=["team"], prefix="/team")
app.include_router(users_router, tags=["users"], prefix="/users")


# start sever from CLI with:
# python -m uvicorn main:app --reload

# run the following code to deploy to fly.io, DO NOT use for dev env
# python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080