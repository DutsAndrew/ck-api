from flask import jsonify

def welcome_request():
    return jsonify({'message': 'Welcome to the ClassKeeper API, please read the docs or use the /api prefix to access relevant data'})

def api_welcome_request():
    return jsonify({'message': 'Using the /api prefix please request the correct data needed'})