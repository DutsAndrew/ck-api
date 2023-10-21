from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ValidationError
from models.color_scheme import UserColorPreferences
from models.calendar import Calendar
from models.bson_object_id import PyObjectId
from bson import ObjectId
import re


class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    account_type: str = Field(default='basic')
    email: EmailStr = Field(required=True)
    calendars: List[PyObjectId] = Field(default_factory=list)
    chats: List[PyObjectId] = Field(default_factory=list)
    classes: List[PyObjectId] = Field(default_factory=list)
    company: str = Field(default_factory=str)
    first_name: str = Field(required=True)
    joined: datetime = Field(default_factory=datetime.now)
    job_title: str = Field(default=str)
    last_contributed: Optional[datetime] = Field(default_factory=datetime.now)
    last_name: str = Field(required=True)
    last_online: datetime = Field(default_factory=datetime.now)
    notes: List[PyObjectId] = Field(default_factory=list)
    notifications_read: List = Field(default_factory=list)
    notifications_unread: List = Field(default_factory=list)
    password: str = Field(required=True)
    pending_calendars: List[PyObjectId] = Field(default_factory=list)
    pending_chats: List[PyObjectId] = Field(default_factory=list)
    pending_tasks: List[PyObjectId] = Field(default_factory=list)
    pending_teams: List[PyObjectId] = Field(default_factory=list)
    personal_calendar: object = Field(default_factory=object)
    tasks: List[PyObjectId] = Field(default_factory=list)
    teams: List[PyObjectId] = Field(default_factory=list)
    total_completed_projects: int = Field(default_factory=int)
    total_completed_tasks: int = Field(default_factory=int)
    total_completed_subtasks: int = Field(default_factory=int)
    user_color_preferences: UserColorPreferences = Field(default_factory=lambda: UserColorPreferences())
    verified_email: bool = Field(default=False)
    yearly_completed_projects: int = Field(default_factory=int)
    yearly_completed_tasks: int = Field(default_factory=int)
    yearly_completed_subtasks: int = Field(default_factory=int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.personal_calendar = Calendar(calendar_type="personal", name=f"{self.first_name}'s Personal Calendar", user_id=self.id)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v:
            raise ValidationError("You cannot create an account without an email address")
        return v
    
    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls, v):
        if not v:
            raise ValidationError("We cannot create your account without a first name entry")
        if len(v) < 1:
            raise ValidationError("Your first name must be at least 1 character")
        if len(v) > 1000:
            raise ValidationError("first name must be no more than 1000 characters")
        if not re.match(r'^[A-Za-z \-\'\.]+$', v):
            raise ValidationError("first name has non-alpha characters")      
        return v
    
    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, v):
        if not v:
            raise ValidationError("We cannot create your account without a last name entry")
        if len(v) < 1:
            raise ValidationError("Your last name must be at least 1 character")
        if len(v) > 1000:
            raise ValidationError("Your last name must be no more than 1000 characters")
        if not re.match(r'^[A-Za-z \-\'\.]+$', v):
            raise ValidationError("Your last name has too many non-alpha characters")    
        return v
    
    @field_validator('password', mode='after')
    @classmethod
    def validate_password(cls, v):
        if not v:
            raise ValidationError("You cannot create an account without adding a password")
        if len(v) < 5:
            raise ValidationError("Your password must be more than 5 characters")
        if len(v) > 100:
            raise ValidationError("your password cannot be more than 100 characters")
        if not re.match(r'^(?=(.*\d.*){2})(?=.*[!@#$%^&*()_+={}[\]:;<>,.?~])', v):
           raise ValidationError("Your password must have at least 2 numbers and 1 symbol")
        return v
    
    @field_validator('job_title', mode='after')
    @classmethod
    def validate_job_title(cls, v):
        if v is not None:
            if len(v) > 50:
                raise ValidationError("Your job title must be no more than 50 characters, FYI this field is not required and can be left blank")
            if not re.match(r'^[A-Za-z \-\'\.]+$', v):
                raise ValidationError("Your job title must be in alpha characters, FYI this field is not required and can be left blank")
        return v
        
    @field_validator('company', mode='after')
    @classmethod
    def validate_company(cls, v):
        if v is not None:
            if len(v) > 50:
                raise ValidationError("Your company name must be no more than 50 characters, FYI this field is not required and can be left blank")         
            if not re.match(r'^[A-Za-z \-\'\.]+$', v):
                raise ValidationError("Your company name must be in alpha characters, FYI this field is not required and can be left blank")
        return v 

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
                "account_type": 'basic',
                "email": "george123@yahoo.com",
                "calendars": [str(ObjectId()), str(ObjectId())],
                "chats": [str(ObjectId()), str(ObjectId())],
                "classes": [str(ObjectId()), str(ObjectId())],
                "company": None,
                "first_name": "Kathy",
                "joined": "2023-07-27 13:27:25.303335",
                "job_title": None,
                "last_contributed": "2023-07-27 13:27:25.303335",
                "last_name": "Bean",
                "last_online": "2023-07-27 13:27:25.303335",
                "notes": [str(ObjectId()), str(ObjectId()), str(ObjectId()), str(ObjectId()), str(ObjectId())],
                "password": "$2b$12$TnK7rTwFqTstmcLLNEtyTuiIRBWBz0k8SNSBCx8yPloZCqkH7uIkG",
                "pending_chats": [],
                "pending_tasks": [],
                "pending_teams": [],
                "tasks": [str(ObjectId()), str(ObjectId())],
                "teams": [str(ObjectId())],
                "total_completed_projects": 0,
                "total_completed_tasks": 0,
                "total_completed_subtasks": 0,
                "user_color_preferences": {
                    "calendars": [
                        {
                            "apply_to_which_object_id": "calendar_id_1",
                            "font_color": "#FF0000",
                            "background_color": "rgb(255, 0, 0)"
                        },
                        {
                            "apply_to_which_object_id": "calendar_id_2",
                            "font_color": "#0000FF",
                            "background_color": "rgb(0, 0, 255)"
                        },
                    ],
                    "chats": [
                        {
                            "apply_to_which_object_id": "chat_id_1",
                            "font_color": "#00FF00",
                            "background_color": "rgb(0, 255, 0)"
                        },
                        {
                            "apply_to_which_object_id": "chat_id_2",
                            "font_color": "#00FF00",
                            "background_color": "rgb(0, 255, 0)"
                        },
                    ],
                    "events": [
                        {
                            "apply_to_which_object_id": "event_id_1",
                            "font_color": "#FFFF00",
                            "background_color": "rgb(255, 255, 0)"
                        },
                        {
                            "apply_to_which_object_id": "event_id_2",
                            "font_color": "#FFFF00",
                            "background_color": "rgb(255, 255, 0)"
                        },
                    ],
                    "teams": [
                        {
                            "apply_to_which_object_id": "team_id_1",
                            "font_color": "#FF00FF",
                            "background_color": "rgb(255, 0, 255)"
                        },
                        {
                            "apply_to_which_object_id": "team_id_2",
                            "font_color": "#FF00FF",
                            "background_color": "rgb(255, 0, 255)"
                        },
                    ],
                    "user": {
                        "font_color": "#000000",
                        "background_color": "#FFFFFF"
                    },
                },
                "verified_email": False,
                "yearly_completed_projects": 0,
                "yearly_completed_tasks": 0,
                "yearly_completed_subtasks": 0,
            }
        }
    }
    
# Example JSON Data that passes Validation:
# {
#   "email": "email@gmail.com",
#   "company": "amazon",
#   "first_name": "John",
#   "last_name": "Krawzinski",
#   "job_title": "Web Developer",
#   "password": "squares101$",
#   "confirm_password": "squares101$"
# }