from fastapi import FastAPI

# import routes
from routes.api_routes import api_router
from routes.app_routes import app_router

app = FastAPI()

app.include_router(app_router)
app.include_router(api_router)

# start server
if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        print(f"error occurred: {e}")