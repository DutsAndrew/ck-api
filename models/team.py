from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid

# Other models needed to create this one
from note import Note
from task import Task
from user import User
from calendar import Calendar
from color_scheme import ColorScheme

# To keep data clean, teams need to hold the majority of the data to keep user data low
## Teams should have the following:

### all tasks that belong to this team
### one calendar per team, no more
### all notes that belong to this team
### all user_id refs of users in this team
### team lead assigned to manage team
### color scheme set by group

class Team(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    calendar: Calendar = Field(required=True)
    color_scheme: Optional[ColorScheme]
    notes: List[Note] = Field(default_factory=list, required=True)
    tasks: List[Task] = Field(default_factory=list, required=True)
    team_lead: str
    users: List[str] = Field(default_factory=list, required=True)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de500-a02a-4b30-b46c-32537c7f1f6e",
                "calendar": "066de501-a02a-4b30-b46c-32537c7f1f6e",
                "color_scheme": {
                    "font_color": "#37D9C8",
                    "background_color": "rgb(55, 217, 200)"
                },
                "notes": ["066de500-a02a-4b30-b46c-32537c7f1f7d", "066de500-a02a-4b30-b46c-32537c7f1f7y"],
                "tasks": ["066de500-a02a-4b30-b46c-12337c7f1f6e", "066de500-a02a-4b30-b46c-98737c7f1f6e"],
                "team_lead": "066de500-a02a-4b30-b46c-32537c6d1f6e",
                "users": ["011de500-a02a-4b30-b46c-32537c7f1f6e", "066de500-a02a-5c30-b46c-32537c7f1f6e"]
            }
        }