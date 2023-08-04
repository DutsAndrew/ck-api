from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationError
from models.color_scheme import UserColorPreferences
from models.bson_object_id import PyObjectId
from bson import ObjectId
import re

class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    account_type: str = Field(default='basic')
    email: EmailStr = Field(required=True)
    calendars: Optional[List[PyObjectId]] = Field(default_factory=list)
    chats: Optional[List[PyObjectId]] = Field(default_factory=list)
    company: Optional[str] = Field(default_factory=None)
    first_name: str = Field(required=True)
    joined: datetime = Field(default_factory=lambda: datetime.now())
    job_title: Optional[str] = Field(default=None)
    last_name: str = Field(required=True)
    last_online: datetime = Field(default_factory=lambda: datetime.now())
    notes: Optional[List[PyObjectId]] = Field(default_factory=list)
    password: str = Field(required=True)
    pending_chats: Optional[List[PyObjectId]] = Field(default_factory=list)
    pending_tasks: Optional[List[PyObjectId]] = Field(default_factory=list)
    pending_teams: Optional[List[PyObjectId]] = Field(default_factory=list)
    tasks: Optional[List[PyObjectId]] = Field(default_factory=list)
    teams: Optional[List[PyObjectId]] = Field(default_factory=list)
    user_color_preferences: UserColorPreferences = Field(default_factory=lambda: UserColorPreferences())
    verified_email: bool = Field(default=False)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # if no email provided return
        if not v:
            raise ValidationError("You cannot create an account without an email address")
        return v
    
        # all other email validation can be done through Pydantic's EmailStr type

    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls, v):
        # if no first name
        if not v:
            raise ValidationError("We cannot create your account without a first name entry")
    
        # if first name is too short
        if len(v) < 1:
            raise ValidationError("Your first name must be at least 1 character")
        
        # if first name is too long
        if len(v) > 1000:
            raise ValidationError("first name must be no more than 1000 characters")
        
        if not re.match(r'^[A-Za-z \-\'\.]+$', v):
            raise ValidationError(" first name has too many non-alpha characters")
            
        return v
    
    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, v):
        # if no last name
        if not v:
            raise ValidationError("We cannot create your account without a last name entry")
    
        # if last name is too short
        if len(v) < 1:
            raise ValidationError("Your last name must be at least 1 character")
        
        # if first name is too long
        if len(v) > 1000:
            raise ValidationError("Your last name must be no more than 1000 characters")
        
        if not re.match(r'^[A-Za-z \-\'\.]+$', v):
            raise ValidationError("Your last name has too many non-alpha characters")
            
        return v
    
    @field_validator('password', mode='after')
    @classmethod
    def validate_password(cls, v):
        # no password
        if not v:
            raise ValidationError("You cannot create an account without adding a password")

        # password is too short
        if len(v) < 5:
            raise ValidationError("Your password must be more than 5 characters")

        # password is too long
        if len(v) > 100:
            raise ValidationError("your password cannot be more than 100 characters")

        # Match at least 2 numbers and 1 symbol
        if not re.match(r'^(?=(.*\d.*){2})(?=.*[!@#$%^&*()_+={}[\]:;<>,.?~])', v):
           raise ValidationError("Your password must have at least 2 numbers and 1 symbol")
        
        return v
    
    # mode='before' runs the validator before value is set on model
    @field_validator('job_title', mode='after')
    @classmethod
    def validate_job_title(cls, v):
        if v is not None:
            # job title was added validate it
            if len(v) < 2:
                raise ValidationError("Your job title entry must be at least 2 characters, FYI this field is not required and can be left blank")

            if len(v) > 50:
                raise ValidationError("Your job title must be no more than 50 characters, FYI this field is not required and can be left blank")

            if not re.match(r'^[A-Za-z \-\'\.]+$', v):
                raise ValidationError("Your job title must be in alpha characters, FYI this field is not required and can be left blank")

        return v
        
    @field_validator('company', mode='after')
    @classmethod
    def validate_company(cls, v):
        if v is not None:
            # company added
            if len(v) < 2:
                raise ValidationError("Your company name entry must be at least 2 characters, FYI this field is not required and can be left blank")

            if len(v) > 50:
                raise ValidationError("Your company name must be no more than 50 characters, FYI this field is not required and can be left blank")
            
            if not re.match(r'^[A-Za-z \-\'\.]+$', v):
                raise ValidationError("Your company name must be in alpha characters, FYI this field is not required and can be left blank")

        return v 


    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "account_type": 'basic',
                "email": "george123@yahoo.com",
                "calendars": [str(ObjectId()), str(ObjectId())],
                "chats": [str(ObjectId()), str(ObjectId())],
                "company": None,
                "first_name": "Kathy",
                "joined": "2023-07-27 13:27:25.303335",
                "job_title": None,
                "last_name": "Bean",
                "last_online": "2023-07-27 13:27:25.303335",
                "notes": [str(ObjectId()), str(ObjectId()), str(ObjectId()), str(ObjectId()), str(ObjectId())],
                "password": "$2b$12$TnK7rTwFqTstmcLLNEtyTuiIRBWBz0k8SNSBCx8yPloZCqkH7uIkG",
                "pending_chats": [],
                "pending_tasks": [],
                "pending_teams": [],
                "tasks": [str(ObjectId()), str(ObjectId())],
                "teams": [str(ObjectId())],
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
                }
            }
        }
    }

class UserLogin(BaseModel):
    email: str
    password: str
    
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