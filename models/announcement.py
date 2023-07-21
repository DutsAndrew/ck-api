from flask import MongoEngine
from datetime import datetime

db = MongoEngine()

# Announcements should have the following:
## when it was created
## what text it needs to send
## how long to display for


class Announcement(db.Document):
  announcement = db.StringField(required=True)
  createdOn = db.DateTimeField(default=datetime.now, required=True)
  displayFor = db.StringField(required=True)