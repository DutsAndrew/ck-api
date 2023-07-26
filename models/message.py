from datetime import datetime

## Messages should have the following:

# user who submitted it
# what time message was created
# whether team members have read it or not
# which chat_id it belongs to

class Message:
    def __init__(self, db, **kwargs):
        # Model for Message
        self.collection = db['messages']  # Use the 'messages' collection

        self.created_by = kwargs.get("created_by")
        self.created_on = kwargs.get("created_on", datetime.now())
        self.which_chat = kwargs.get("which_chat")
        self.who_has_read = kwargs.get("who_has_read", [])

    def to_dict(self):
        return {
            "created_by": self.created_by,
            "created_on": self.created_on,
            "which_chat": self.which_chat,
            "who_has_read": self.who_has_read,
        }

    # Save the message to the database
    async def save(self):
        result = await self.collection.insert_one(self.to_dict())
        return result.inserted_id

    # Fetch a message by its ObjectID
    @classmethod
    async def find_by_id(cls, db, message_id):
        collection = db['messages']  # Use the 'messages' collection
        message_data = await collection.find_one({"_id": message_id})
        if message_data:
            return cls(db, **message_data)
        return None