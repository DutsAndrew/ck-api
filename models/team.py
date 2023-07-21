from flask import MongoEngine

db = MongoEngine()

# To keep data clean, teams need to hold the majority of the data to keep user data low
## Teams should have the following:

### all tasks that belong to this team
### one calendar per team, no more
### all notes that belong to this team
### all user_id refs of users in this team
### team lead assigned to manage team
### color scheme set by group

class Team(db.Document):
    calendar = db.ReferenceField('Calendar', required=True)
    colorScheme = db.StringField(required=False)
    notes = db.ListField(db.ReferenceField('Note', required=True))
    tasks = db.ListField(db.ReferenceField('Task'), required=True)
    teamLead = db.ReferenceField('User', required=True)
    users = db.ListField(db.ReferenceField('User'), required=True)