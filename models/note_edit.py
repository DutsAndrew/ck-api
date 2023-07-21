from flask import MongoEngine
from datetime import datetime

db = MongoEngine()

class NoteEdit(db.Document):
    editedBy = db.ReferenceField('User', required=True)
    newEntry = db.StringField(required=True)
    oldEntry = db.StringField(required=True)
    createdOn = db.DateTimeField(default=datetime.now, required=True)