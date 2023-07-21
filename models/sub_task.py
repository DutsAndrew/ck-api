from flask import MongoEngine
from datetime import datetime

db = MongoEngine()

## Sub tasks should have the following:

# task it is assigned to
# completion status (yes/no)
# when subtask was created
# when subtask was completed
# users assigned to sub task

class SubTask(db.Document):
    assignedTo = db.ListField(db.ReferenceField('User'), required=True)
    completed = db.BooleanField(default=False, required=True)
    completedOn = db.DateTimeField(required=False)
    createdOn = db.DateTimeField(default=datetime.now, required=True)
    task = db.ReferenceField('Task', required=True)