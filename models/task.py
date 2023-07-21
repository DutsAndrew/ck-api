from flask import MongoEngine
from datetime import datetime

db = MongoEngine()

# Tasks should have the following:

## what team if any it belongs to
## which user(s) it is currently assigned to
## what time it was created
## what time it needs to be completed
## what time it was completed
## status of completion
## array of sub-tasks if chosen
## colorscheme set by group

class Task(db.Document):
    assignedTo= db.ListField(db.ReferenceField('User'), required=True)
    colorScheme = db.StringField(required=False)
    completeBy = db.DateTimeField(required=True)
    completedOn = db.DateTimeField(required=False)
    completed = db.BooleanField(default=False, required=True)
    createdOn = db.DateTimeField(default=datetime.now, required=True)
    team = db.ReferenceField('Team', required=True)