from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
from models.bson_object_id import PyObjectId
from bson import ObjectId
import calendar
import holidays

## Calendars should have the following:
# what team or user the calendar belongs to
# what events have been created and added to calendar
# what year the calendar is for
# color scheme set by user

class Calendar(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    authorized_users: List[PyObjectId] = Field(default_factory=list)
    calendar_years_and_dates: dict = Field(default_factory=dict)
    calendar_holidays: list = Field(default_factory=list)
    calendar_type: str = Field(default_factory=str)
    created_by: PyObjectId = Field(default_factory=PyObjectId)
    created_on: datetime = Field(default_factory=datetime.now)
    events: list = Field(default_factory=list)
    name: str = Field(default_factory=str)
    pending_users: list = Field(default_factory=list)
    view_only_users: list = Field(default_factory=list)


    def __init__(self, calendar_type, name, userId: PyObjectId, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.authorized_users = [userId]
        self.calendar_type = calendar_type
        self.created_by = userId
        self.name = name


    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str,
            PyObjectId: str,
            datetime: lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S')
          },
        "json_schema_extra": {
            "example": {
                "accompanied_team": None,
                "accompanied_user": str(ObjectId()),
                "events": [str(ObjectId()), str(ObjectId())],
                "type": 'account / team',
                "year": 2023,
            }
        }
    }