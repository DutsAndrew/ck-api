from dotenv import dotenv_values
import os

def get_jwt_env_variables():
    dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    config = dotenv_values(dotenv_path)

    jwt_config = {
        "JWT_SECRET": config["JWT_SECRET"],
        "JWT_ALGORITHM": config["JWT_ALGORITHM"],
    }
    
    return jwt_config