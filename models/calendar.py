from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

## Calendars should have the following:
# what team or user the calendar belongs to
# what events have been created and added to calendar
# what year the calendar is for
# color scheme set by user

# CALENDARS MUST BE ACCOMPANIED BY A USER OR TEAM _ID BUT NOT BOTH

class Calendar(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    accompanied_team: str = Field(default_factory=None, required=True)
    accompanied_user: str = Field(default_factory=None, required=True)
    events: List[str] = Field(default_factory=list, required=True)
    year: int = Field(default_factory=lambda: datetime.now().year, required=True)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f2z",
                "accompanied_team": None,
                "accompanied_user": "066de609-b04a-4b30-b46c-32537c7f1f2z",
                "events": ["066de609-b04a-4b30-b46c-32537c7f1f2s", "066de609-b04a-4b30-b46c-32537c7f1f2f"],
                "year": 2023,
            }
        }