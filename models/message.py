from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId

## Messages should have the following:

# user who submitted it
# what time message was created
# whether team members have read it or not
# which chat_id it belongs to

class Message(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    accompanied_chat: PyObjectId = Field(None)
    created_by: PyObjectId = Field(None)
    created_on: datetime = Field(default_factory=lambda: datetime.now, required=True)
    who_has_read: Optional[List[PyObjectId]] = Field(default_factory=list, required=True)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "accompanied_chat": str(ObjectId()),
                "created_by": str(ObjectId()),
                "created_on": "2023-07-27 13:27:25.303335",
                "who_has_read": [str(ObjectId()), str(ObjectId())],
            }
        }
    }