from fastapi import FastAPI
from dotenv import dotenv_values
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# import routes
from routes.api_routes import api_router
from routes.app_routes import app_router

# get .env files
config = dotenv_values(".env")

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(config["MONGO_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to MongoDB!")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(app_router)
app.include_router(api_router, tags=["api"], prefix="/api")

# start sever from CLI with:
# python -m uvicorn main:app --reload