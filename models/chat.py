from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
import uuid

## Chats should have the following:

# user(s) in the chat
# all message id's of messages sent in chat
# last message received on: _____
# color_scheme set by group

class Chat(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    last_message: datetime = Field(default_factory=lambda: datetime.now(), required=True)
    messages: List[str] = Field(default_factory=list, required=True)
    users: List[str] = Field(default_factory=list, required=True)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "055de609-b04a-4b30-b46c-32537c7f1f6e",
                "messages": ["055de609-a14a-4b30-b46c-32537c7f1f6e"],
                "last_message": "2023-07-27 13:27:25.303335",
                "users": ["066de609-b04a-4b30-b46c-32537c7f1f6d", "066de609-b04a-4b30-b46c-32537c7f1f6z", "066de609-b04a-4b30-b46c-32537c7f1f6e"],
            }
        }