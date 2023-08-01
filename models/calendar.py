from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId

## Calendars should have the following:
# what team or user the calendar belongs to
# what events have been created and added to calendar
# what year the calendar is for
# color scheme set by user

# CALENDARS MUST BE ACCOMPANIED BY A USER OR TEAM _ID BUT NOT BOTH

class Calendar(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    accompanied_team: Optional[PyObjectId] = Field(default_factory=None, alias="team_id")
    accompanied_user: Optional[PyObjectId] = Field(default_factory=None, alias="user_id")
    events: Optional[List[PyObjectId]] = Field(default_factory=list)
    year: int = Field(default_factory=lambda: datetime.now.year, required=True)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "accompanied_team": None,
                "accompanied_user": str(ObjectId()),
                "events": [str(ObjectId()), str(ObjectId())],
                "year": 2023,
            }
        }
    }