from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

# other models needed to create this one
from color_scheme import UserColorPreferences

class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    account_type: str = Field(default='basic', required=True)
    email: str = Field(required=True)
    calendars: List[str] = Field(default_factory=list, required=True)
    chats: List[str] = Field(default_factory=list, required=True)
    company: Optional[str] = Field(default=None)
    joined: datetime = Field(default_factory=lambda: datetime.now(), required=True)
    job_title: Optional[str] = Field(default=None)
    last_online: datetime = Field(default_factory=lambda: datetime.now(), required=True)
    notes: List[str] = Field(default_factory=list, required=True)
    tasks: List[str] = Field(default_factory=list, required=True)
    teams: List[str] = Field(default_factory=list, required=True)
    user_color_preferences: UserColorPreferences

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "account_type": 'basic',
                "email": "george123@yahoo.com",
                "calendars": ['066de609-b04a-4b30-b46c-32537c7f1f6e', '066de609-b04a-4b30-b46c-32537c7f1f6a'],
                "chats": ["066de609-b04a-4b30-b46c-32537c7f1g6e", "066de609-b04a-4b30-b46c-32537c7h1f6e"],
                "company": None,
                "joined": "2023-07-27 13:27:25.303335",
                "job_title": None,
                "last_online": "2023-07-27 13:27:25.303335",
                "notes": ["166de609-b04a-4b30-b32c-32537c7f1f6e"],
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