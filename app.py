from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# import routes
from routes.api_routes import api_blueprint
from routes.app_routes import app_blueprint

app = Flask(__name__)
CORS(app)

# define routes

app.register_blueprint(app_blueprint)
app.register_blueprint(api_blueprint)

# start server
if __name__ == "__main__":
    app.run(debug=True)

