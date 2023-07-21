from flask import MongoEngine
from datetime import datetime

db = MongoEngine()

## Chats should have the following:

# user(s) in the chat
# all message id's of messages sent in chat
# last message received on: _____
# colorscheme set by group

class Chat(db.Document):
    colorScheme = db.StringField(required=False)
    createdOn = db.DateTimeField(default=datetime.now, required=True)
    messages = db.ListField(db.ReferenceField('Message'), required=True)
    users = db.ListField(db.ReferenceField('User'), required=True)