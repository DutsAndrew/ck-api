from models.color_scheme import UserColorPreferences

async def welcome_request():
    new_scheme = UserColorPreferences()
    return {'message': "Welcome to the API"}

async def api_welcome_request():
    return {'message': 'Using the /api prefix please request the correct data needed'}