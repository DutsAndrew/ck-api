from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import asyncio
import motor.motor_asyncio
import os

# load env variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# get MONGO_URI from env
MONGO_URI = os.getenv("MONGO_URI")

# link in to db
async def connect_to_db():
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        db = client.get_database()
        return db
    except Exception as e:
        raise Exception("Failed to connect to MongoDB") from e
    
# import routes
from routes.api_routes import api_blueprint
from routes.app_routes import app_blueprint

# define routes
app.register_blueprint(app_blueprint)
app.register_blueprint(api_blueprint)

# start server
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        db = loop.run_until_complete(connect_to_db())
        print("Connected to db successfully")
    except Exception as e:
        print("Error:", e)

    
    app.run(debug=True)