from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator, ValidationError
import uuid
import re

# other models needed to create this one
from models.color_scheme import UserColorPreferences

class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    account_type: str = Field(default='basic')
    email: EmailStr = Field(required=True)
    calendars: List[str] = Field(default_factory=list)
    chats: List[str] = Field(default_factory=list)
    company: Optional[str] = Field(default_factory=None)
    first_name: str = Field(required=True)
    joined: datetime = Field(default_factory=lambda: datetime.now())
    job_title: Optional[str] = Field(default=None)
    last_name: str = Field(required=True)
    last_online: datetime = Field(default_factory=lambda: datetime.now())
    notes: List[str] = Field(default_factory=list)
    password: str
    tasks: List[str] = Field(default_factory=list)
    teams: List[str] = Field(default_factory=list)
    user_color_preferences: UserColorPreferences

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "account_type": 'basic',
                "email": "george123@yahoo.com",
                "calendars": ['066de609-b04a-4b30-b46c-32537c7f1f6e', '066de609-b04a-4b30-b46c-32537c7f1f6a'],
                "chats": ["066de609-b04a-4b30-b46c-32537c7f1g6e", "066de609-b04a-4b30-b46c-32537c7h1f6e"],
                "company": None,
                "first_name": "Kathy",
                "joined": "2023-07-27 13:27:25.303335",
                "job_title": None,
                "last_name": "Bean",
                "last_online": "2023-07-27 13:27:25.303335",
                "notes": ["166de609-b04a-4b30-b32c-32537c7f1f6e"],
                "password_hashed": "$2b$12$TnK7rTwFqTstmcLLNEtyTuiIRBWBz0k8SNSBCx8yPloZCqkH7uIkG",
                "tasks": ["166de609-b04a-4b30-b46c-32537c7f1f6e", "266de609-b04a-4b30-b46c-32537c7f1f6e"],
                "teams": ["033de609-b04a-4b30-b46c-32537c7f1f6e", "099de609-b04a-4b30-b46c-32537c7f1f6e"],
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

    @validator('email')
    def validate_email(cls, v):
        # if no email provided return
        if not v:
            raise ValidationError("You cannot create an account without an email address")
        return v
    
        # all other email validation can be done through Pydantic's EmailStr type

    @validator('first_name')
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
        
        if not v.isAlpha():
            raise ValidationError(" first name has too many non-alpha characters")
            
        return v
    
    @validator('last_name')
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
        
        if not v.isAlpha():
            raise ValidationError("Your last name has too many non-alpha characters")
            
        return v
    
    @validator('password')
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
        pattern = r'^(?=(.*\d){2})(?=.*[!@#$%^&*()_+={}[\]:;<>,.?~])'
        if not re.match(pattern, v):
            raise ValidationError("Your password must have at least 2 numbers and 1 symbol")
        
        return v
    
    # pre=True runs the validator before value is set on model
    @validator('job_title', pre=True)
    def validate_job_title(cls, v):
        if v is not None:
            # job title was added validate it
            if len(v) < 2:
                raise ValidationError("Your job title entry must be at least 2 characters, FYI this field is not required and can be left blank")

            if len(v) > 50:
                raise ValidationError("Your job title must be no more than 50 characters, FYI this field is not required and can be left blank")

            if not v.isAlpha():
                raise ValidationError("Your job title must be in alpha characters, FYI this field is not required and can be left blank")

            return v
        
    @validator('company', pre=True)
    def validate_company(cls, v):
        if v is not None:
            # company added
            if len(v) < 2:
                raise ValidationError("Your company name entry must be at least 2 characters, FYI this field is not required and can be left blank")

            if len(v) > 50:
                raise ValidationError("Your company name must be no more than 50 characters, FYI this field is not required and can be left blank")
            
            if not v.isAlpha():
                raise ValidationError("Your company name must be in alpha characters, FYI this field is not required and can be left blank")