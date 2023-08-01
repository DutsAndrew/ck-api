from fastapi import FastAPI
from dotenv import dotenv_values
from motor.motor_asyncio import AsyncIOMotorClient

# import routes
from routes.api_routes import api_router
from routes.app_routes import app_router

# get .env files
config = dotenv_values(".env")

app = FastAPI()

def get_app_for_testing():
    mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
    app.mongo_client = mongo_client  # Set the mongo_client attribute

async def setup_db_client():
    app.mongodb_client = AsyncIOMotorClient(config["MONGO_URI"])
    app.db = app.mongodb_client[config["DB_NAME"]]
    print("Connected to MongoDB!")
    return app # return app instance after setting up db for testing files

async def shutdown_db_client():
    app.mongodb_client.close()

@app.on_event("startup")
async def startup_event():
    await setup_db_client()

@app.on_event("shutdown")
async def shutdown_event():
    await shutdown_db_client()

app.include_router(app_router)
app.include_router(api_router, tags=["api"], prefix="/api")

# start sever from CLI with:
# python -m uvicorn main:app --reload

# run the following code to deploy to fly.io, DO NOT use for dev env
# python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080