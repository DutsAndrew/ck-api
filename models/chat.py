from datetime import datetime

## Chats should have the following:

# user(s) in the chat
# all message id's of messages sent in chat
# last message received on: _____
# color_scheme set by group

class Chat:
    def __init__(self, db, **kwargs):
        # Model for Chat
        self.collection = db['chats']  # Use the 'chats' collection

        self.color_scheme = kwargs.get("color_scheme")
        self.created_on = kwargs.get("created_on", datetime.now())
        self.messages = kwargs.get("messages", [])
        self.users = kwargs.get("users", [])

    def to_dict(self):
        return {
            "color_scheme": self.color_scheme,
            "created_on": self.created_on,
            "messages": [message.to_dict() for message in self.messages],
            "users": self.users,
        }

    # Save the chat to the database
    async def save(self):
        result = await self.collection.insert_one(self.to_dict())
        return result.inserted_id

    # Fetch a chat by its ObjectID
    @classmethod
    async def find_by_id(cls, db, chat_id):
        collection = db['chats']  # Use the 'chats' collection
        chat_data = await collection.find_one({"_id": chat_id})
        if chat_data:
            return cls(db, **chat_data)
        return None