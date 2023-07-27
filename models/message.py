from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
import uuid

## Messages should have the following:

# user who submitted it
# what time message was created
# whether team members have read it or not
# which chat_id it belongs to

class Message(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    accompanied_chat: str = Field(required=True)
    created_by: str = Field(required=True)
    created_on: datetime = Field(default_factory=lambda: datetime.now(), required=True)
    who_has_read: List[str] = Field(default_factory=list, required=True)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-99004c7f1f6e",
                "accompanied_chat": "066de609-a15b-4b30-b46c-99004c7f1f6e",
                "created_by": "126de609-a15b-4b30-b46c-99004c7f1f6e",
                "created_on": "2023-07-27 13:27:25.303335",
                "who_has_read": ["136de609-a15b-4b30-b46c-99004c7f1f6e", "156de609-a15b-4b30-b46c-99004c7f1f6e"],
            }
        }