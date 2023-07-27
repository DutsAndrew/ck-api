from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
import uuid

## Notes should have the following:

# Who created note
# What team note belongs to
# When note was created
# Who has made edits to the notes and what changes did they make
# On what day the note was created
# saved notes should be added to team's calendar
# colorscheme set by group

# EACH NOTE MUST BE ASSIGNED TO EITHER A TEAM OR USER, BUT NOT BOTH

class Note(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    assigned_team: str = Field(default_factory=None)
    assigned_user: str = Field(default_factory=None)
    created_on: datetime = Field(default_factory=lambda: datetime.now(), required=True)
    edits: List[str] = Field(default_factory=list, required=True)
    note: str = Field(required=True)
    who_created: str = Field(required=True)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7c2c5n",
                "assigned_team": "066de609-b04a-4b30-b46c-32537c7c2c5o",
                "assigned_user": None,
                "created_on": "2023-07-27 13:27:25.303335",
                "edits": ["066de609-b04a-4b30-b46c-32537c7c2c5p", "066de609-b04a-4b30-b46c-32537c7c2c5q"],
                "note": "<h1>6th Team Meeting</h1><br><p>We talked about nothing</p>",
                "who_created": "066de609-b04a-4b30-b46c-32537c7c2c5r",
            }
        }