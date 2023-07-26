from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient

# import routes
from routes.api_routes import api_router
from routes.app_routes import app_router

# get .env files
config = dotenv_values(".env")

app = FastAPI()

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["MONGO_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to MongoDB!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(app_router)
app.include_router(api_router)

# start sever from CLI with:
# python -m uvicorn main:app --reload