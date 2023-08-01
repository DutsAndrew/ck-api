from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId

# Notifications must be able to do the following:
# store whether it belongs to a team, chat, calendar, or user
# store the id of who/what it belongs to

class Notification(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    notification: str = Field(required=True)
    notification_type: str # team, chat, calendar, user
    notified: bool = Field(False)
    notify_who: PyObjectId = Field(required=True)
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "notification": "Jack made an edit to Note titled: 'Team Meeting'",
                "notification_type": "Team",
                "notified": False,
                "notify_who": str(ObjectId()),
                "timestamp": "2023-07-27 13:27:25.303335",
            }
        }
    }