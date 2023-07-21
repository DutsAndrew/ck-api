from flask import MongoEngine

db = MongoEngine()

# Events should have the following:

# which calendar they belong to
# which user created it
# any patterns (weekly, daily, monthly, etc)
# color-scheme set by user

class Event(db.Document):
    calendar = db.ReferenceField('Calendar', required=True)
    colorScheme = db.StringField(required=False)
    createdBy = db.ReferenceField('User', required=True)
    patterns = db.ListField(db.StringField(), required=True)