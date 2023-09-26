from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId
from typing import Optional
from datetime import datetime

# Events should have the following:

# which calendar they belong to
# which user created it
# any patterns (weekly, daily, monthly, etc)
# color-scheme set by user

class Event(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    calendar: Optional[PyObjectId] = Field(None)
    created_by: Optional[PyObjectId] = Field(None)
    event_date_and_time: datetime = Field(default_factory=datetime.now, required=True)
    event_description: str = Field(default_factory=str)
    event_name: str = Field(default_factory=str, required=True)
    patterns: Optional[str] = Field(None)
    repeats: bool = Field(default_factory=False)


    model_config= {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "calendar": str(ObjectId()),
                "created_by": str(ObjectId()),
                "patterns": None,
            }
        }
    }