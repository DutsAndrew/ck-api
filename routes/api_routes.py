from flask import Blueprint
from controllers import account_controller, announcements_controller
from controllers import app_controller, auth_controller
from controllers import calendar_controller, jenkins_ai_controller
from controllers import messaging_controller, notes_controller, pages_controller
from controllers import tasks_controller, teams_controller

# all /api prefixed routes will go here
api_blueprint = Blueprint('api', __name__, url_prefix='/api')

api_blueprint.route('/', methods=["GET"])(app_controller.api_welcome_request)

api_blueprint.route('/signup', methods=["POST"])(auth_controller.sign_up)