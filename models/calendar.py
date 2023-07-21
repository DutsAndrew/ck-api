from flask import MongoEngine

db = MongoEngine()

## Calendars should have the following:
# what team or user the calendar belongs to
# what events have been created and added to calendar
# what year the calendar is for
# color scheme set by user

class Calendar(db.Document):
    colorScheme = db.StringField(required=False)
    events = db.ListField(db.ReferenceField('Event'), required=True)
    team = db.ReferenceField('Team', required=False)
    user = db.ReferenceField('User', required=False)
    year = db.IntField(required=True)