from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from models.bson_object_id import PyObjectId
from bson import ObjectId
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class UserRef(BaseModel):
    first_name: str
    last_name: str
    user_id: str = Field(default_factory=str)


class Event(BaseModel):
    id: PyObjectId | str = Field(default_factory=PyObjectId, alias="_id") # string type for when updating an event, so new id isn't created
    calendar_id: str = Field(default_factory=str, required=True)
    combined_date_and_time: Optional[datetime]
    created_by: UserRef
    event_date: datetime = Field(default_factory=datetime.now, required=True)
    event_description: Optional[str] = Field(default_factory=str)
    event_name: str = Field(default_factory=str, required=True)
    event_time: str = Field(default_factory=str)
    repeat_option: str = Field(default_factory=str)
    repeats: Optional[bool] = Field(default_factory=False)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str,
            datetime: lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S')
        }


class CalendarNote(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    calendar_id: str = Field(default_factory=str, required=True)
    created_by: UserRef = Field(default_factory=dict)
    created_on: datetime = Field(default_factory=datetime.now)
    note: str = Field(default_factory=str, required=True)
    start_date: datetime = Field(default_factory=datetime.now, required=True)
    end_date: datetime = Field(default_factory=datetime.now, required=True)
    type: str = Field(default_factory=str, required=True)

    def __init__(
            self,
            calendar_id: str,
            note: str,
            type: str,
            user_ref: UserRef,
            start_date: datetime,
            end_date: datetime,
            id=None,
            *args,
            **kwargs
        ):
            super().__init__(*args, **kwargs)
            self.calendar_id = calendar_id
            self.created_by = user_ref
            self.end_date = end_date
            self.note = note
            self.start_date = start_date
            self.type = type

            if id is not None:
                  self.id = id

    @validator('start_date', 'end_date', pre=True, always=True)
    def serialize_datetime(cls, v):
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        return v

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str,
            datetime: lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S')
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
    
# CALENDAR TYPES CAN BE THE FOLLOWING:
    # PERSONAL - EACH USER HAS ONE
    # TEAM - JUST A CALENDAR CREATED BY ANY USER THAT THEY CAN INVITE OTHERS TO
    # TEAM-CALENDAR - DEFAULT CALENDAR THAT IS CREATED TO PAR WITH EACH CREATED TEAM

class Calendar(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    authorized_users: List[PyObjectId] = Field(default_factory=list)
    calendar_color: str = Field(default_factory=str)
    calendar_notes: List[CalendarNote] = Field(default_factory=list)
    calendar_type: str = Field(default_factory=str)
    created_by: PyObjectId = Field(default_factory=PyObjectId)
    created_on: datetime = Field(default_factory=datetime.now)
    events: List[Event] = Field(default_factory=list)
    name: str = Field(default_factory=str)
    pending_users: List[PendingUser] = Field(default_factory=list)
    team_id: str = Field(default_factory=str) # only needed for team-calendar instance's, see notes above for details
    view_only_users: list = Field(default_factory=list)


    def __init__(
        self,
        calendar_color: str,
        calendar_type: str,
        name: str,
        user_id: PyObjectId,
        pending_users: List[PendingUser] = [],
        team_id=None,
        *args, 
        **kwargs
      ):
          super().__init__(*args, **kwargs)

          if calendar_type == 'team' or 'team-calendar':
              self.pending_users = pending_users

          if calendar_type == 'team-calendar':
              self.team_id = team_id

          self.authorized_users.append(user_id)
          self.calendar_color = calendar_color
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
    }