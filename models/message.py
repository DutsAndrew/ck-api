from flask import MongoEngine
from datetime import datetime

db = MongoEngine()

## Messages should have the following:

# user who submitted it
# what time message was created
# whether team members have read it or not
# which chat_id it belongs to

class Message(db.Document):
    createdBy = db.ReferenceField('User', required=True)
    createdOn = db.DateTimeField(default=datetime.now, required=True)
    whichChat = db.ReferenceField('Chat', required=True)
    whoHasRead = db.ListField(db.ReferenceField('User'), required=True)