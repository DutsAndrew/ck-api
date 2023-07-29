from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid

## what team if any it belongs to
## which user(s) it is currently assigned to
## what time it was created
## what time it needs to be completed
## what time it was completed
## status of completion
## array of sub-tasks if chosen
## color_scheme set by group

class Task(BaseModel):
  id: str = Field(default_factory=uuid.uuid4, alias="_id")
  assigned_to: str = Field(default_factory=None)
  complete_by: Optional[datetime]
  completed_on: Optional[datetime]
  completed: bool = Field(default_factory=False)
  created_on: datetime = Field(default_factory=lambda: datetime.now())
  team: Optional[str] = Field(default_factory=None)

  class Config:
    populate_by_name = True
    json_schema_extra = {
        "example": {
          "_id": "066de609-b04a-0j85-b46c-32537c7f1f6e",
          "assigned_to": "166de609-b04a-0j85-b46c-32537c7f1f6e",
          "complete_by": "2023-07-27 13:27:25.303335",
          "completed": False,
          "created_on": "2023-07-27 13:27:25.303335",
          "team": "066de609-b04a-0j85-b46c-31137c7f1f6",
        }
    }