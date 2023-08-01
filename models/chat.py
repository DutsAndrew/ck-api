from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId

## Chats should have the following:

# user(s) in the chat
# all message id's of messages sent in chat
# last message received on: _____
# color_scheme set by group

class Chat(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    last_message: Optional[datetime] = Field(default_factory=lambda: datetime.now)
    messages: Optional[List[PyObjectId]] = Field(default_factory=list)
    users: Optional[List[PyObjectId]] = Field(default_factory=list)
    pending_users: Optional[List[PyObjectId]] = Field(None)

    mode_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str}, # Map ObjectId to the str encoder func
        "json_schema_extra": {
            "example": {
                "messages": [str(ObjectId())],
                "last_message": "2023-07-27 13:27:25.303335",
                "users": [str(ObjectId()), str(ObjectId()), str(ObjectId())],
                "pending_users": [str(ObjectId())],
            }
        }
    }