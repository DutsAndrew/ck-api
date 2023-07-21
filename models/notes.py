from flask import MongoEngine
from datetime import datetime

db = MongoEngine()

## Notes should have the following:

# Who created note
# What team note belongs to
# When note was created
# Who has made edits to the notes and what changes did they make
# On what day the note was created
# saved notes should be added to team's calendar
# colorscheme set by group

class Notes(db.Document):
    assignedTeam = db.ReferenceField('Team', required=True)
    edits = db.ListField(db.ReferenceField('NoteEdit'), required=True)
    createdOn = db.DateTimeField(default=datetime.now, required=True)
    whoCreated = db.ReferenceField('User', required=True)
    