from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId

# Announcements should have the following:
## when it was created
## what text it needs to send
## how long to display for

class Announcement(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    announcement: str = Field(required=True)
    created_on: datetime = Field(default_factory=lambda: datetime.now, required=True)
    display_for: timedelta = Field(default_factory=lambda: timedelta(weeks=2), required=True)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "announcement": "This is a new feature, enjoy!",
                "created_on": "2023-07-27 13:27:25.303335",
                "display_for": "2w",
            }
        }
    }