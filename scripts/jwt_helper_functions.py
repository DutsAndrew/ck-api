def get_jwt_env_variables():
    from dotenv import dotenv_values
    config = dotenv_values('.env')
    jwt_config = {
        "JWT_SECRET": config["JWT_SECRET"],
        "JWT_ALGORITHM": config["JWT_ALGORITHM"],
    }
    return jwt_config