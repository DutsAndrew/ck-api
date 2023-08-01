from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId
from typing import Optional

# Events should have the following:

# which calendar they belong to
# which user created it
# any patterns (weekly, daily, monthly, etc)
# color-scheme set by user

class Event(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    calendar: Optional[PyObjectId] = Field(None)
    created_by: Optional[PyObjectId] = Field(None)
    patterns: Optional[str] = Field(None)

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