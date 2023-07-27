from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

# other models needed to create this one
from calendar import Calendar
from task import Task
from team import Team
from color_scheme import ColorScheme

class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    email: str = Field(required=True)
    account_type: str = Field(default='basic', required=True)
    calendars: List[Calendar] = Field(default_factory=list, required=True)
    color_scheme: Optional[ColorScheme]
    company: Optional[str] = Field(default=None)
    joined: datetime = Field(default_factory=datetime.now, required=True)
    job_title: Optional[str] = Field(default=None)
    last_online: datetime = Field(default_factory=datetime.now, required=True)
    tasks: List[Task] = Field(default_factory=list, required=True)
    teams: List[Team] = Field(default_factory=list, required=True)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "email": "george123@yahoo.com",
                "account_type": 'basic',
                "calendars": ['066de609-b04a-4b30-b46c-32537c7f1f6e', '066de609-b04a-4b30-b46c-32537c7f1f6a'],
                "color_scheme": {
                    "font_color": "#37D9C8",
                    "background_color": "rgb(55, 217, 200)"
                },
                "company": None,
                "joined": "2023-07-27 13:27:25.303335",
                "job_title": None,
                "last_online": "2023-07-27 13:27:25.303335",
                "tasks": ["166de609-b04a-4b30-b46c-32537c7f1f6e", "266de609-b04a-4b30-b46c-32537c7f1f6e"],
                "teams": ["033de609-b04a-4b30-b46c-32537c7f1f6e", "099de609-b04a-4b30-b46c-32537c7f1f6e"],
            }
        }