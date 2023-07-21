from flask import Blueprint
from controllers import app_controller

app_blueprint = Blueprint('app', __name__)
app_blueprint.route('/', methods=["GET"])(app_controller.welcome_request)