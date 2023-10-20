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

class PendingUser(BaseModel):
    type: str = Field(default_factory=str) # 'authorized' or 'view_only'
    user_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {
            PyObjectId: str,
          },
    }
    

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
    pending_users: List[PendingUser] = Field(default_factory=list)
    view_only_users: list = Field(default_factory=list)


    def __init__(
        self,
        calendar_type,
        name,
        userId: PyObjectId,
        authorized_users=None,
        view_only_users=None, 
        *args, 
        **kwargs
      ):
          super().__init__(*args, **kwargs)

          if calendar_type == 'personal':
              self.authorized_users[userId]

          if calendar_type == 'team':
              self.authorized_users = authorized_users
              self.view_only_users = view_only_users

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