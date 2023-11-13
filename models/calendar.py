from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from models.bson_object_id import PyObjectId
from models.event import Event
from bson import ObjectId

## Calendars should have the following:
# what team or user the calendar belongs to
# what events have been created and added to calendar
# what year the calendar is for
# color scheme set by user

class CalendarNote(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id') # ID IS NOTE FOR STORING IN DB, IT'S FOR SORTING BY UNIQUE ID IF NECESSARY
    created_by: PyObjectId = Field(default_factory=PyObjectId)
    created_on: datetime = Field(default_factory=datetime.now)
    note: str = Field(default_factory=str, required=True)
    start_date: datetime = Field(default_factory=str)
    end_date: datetime = Field(default_factory=str)
    type: str = Field(default_factory=str, required=True)

    def __init__(self, note, type, user_id, date_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.note = note
        self.type = type
        self.created_by = user_id

        ## CREATE METHODS TO TAKE NOTE 'TYPE' AND 'DATE_DATA' AND CREATE DATE TIME OBJECTS FOR 'START_DATE' AND 'END_DATE'

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str,
            PyObjectId: str,
            datetime: lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S')
          },
    }


class PendingUser(BaseModel):
    type: str = Field(default_factory=str) # 'authorized' or 'view_only'
    user_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    def __init__(self, type, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = type
        self.user_id = user_id

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {
            PyObjectId: str,
          },
    }
    

class Calendar(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    authorized_users: List[PyObjectId] = Field(default_factory=list)
    calendar_notes: List[CalendarNote] = Field(default_factory=list)
    calendar_type: str = Field(default_factory=str)
    created_by: PyObjectId = Field(default_factory=PyObjectId)
    created_on: datetime = Field(default_factory=datetime.now)
    events: List[Event] = Field(default_factory=list)
    name: str = Field(default_factory=str)
    pending_users: List[PendingUser] = Field(default_factory=list)
    view_only_users: list = Field(default_factory=list)


    def __init__(
        self,
        calendar_type,
        name,
        user_id: PyObjectId,
        pending_users=None,
        *args, 
        **kwargs
      ):
          super().__init__(*args, **kwargs)

          if calendar_type == 'team':
              self.pending_users = pending_users

          self.authorized_users.append(user_id)
          self.calendar_type = calendar_type
          self.created_by = user_id
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