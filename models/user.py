from flask_mongoengine import MongoEngine

db = MongoEngine()

# users need access to:

## array of teams they are in
## array of calendars refs they are a part of
## array of task refs user is assigned from all groups

class User(db.Document):
    accountType = db.StringField(required=True)
    calendars = db.ListField(db.ReferenceField('Calendar'), required=True)
    email = db.StringField(required=True)
    firstName = db.StringField(required=True)
    joined = db.StringField(required=True)
    lastName = db.StringField(required=True)
    lastOnline = db.StringField(required=True)
    password = db.StringField(required=True)
    role = db.StringField(required=True)
    tasks = db.ListField(db.ReferenceField('Task'), required=True)
    teams = db.ListField(db.ReferenceField('Team'), required=True)