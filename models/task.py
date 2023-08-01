from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId

## what team if any it belongs to
## which user(s) it is currently assigned to
## what time it was created
## what time it needs to be completed
## what time it was completed
## status of completion
## array of sub-tasks if chosen
## color_scheme set by group

class Task(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    assigned_to: Optional[List[PyObjectId]] = Field(None)
    accepted_by: Optional[List[PyObjectId]] = Field(None)
    complete_by: Optional[datetime]
    completed_on: Optional[datetime]
    completed: bool = Field(False)
    completion_rate: int = Field(0)
    created_on: datetime = Field(default_factory=lambda: datetime.now)
    sub_tasks: Optional[List[PyObjectId]] = Field(None)
    team: Optional[PyObjectId] = Field(None)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
              "assigned_to": [str(ObjectId()), str(ObjectId()), str(ObjectId())],
              "accepted_by": [str(ObjectId()), str(ObjectId()), str(ObjectId())],
              "complete_by": "2023-07-27 13:27:25.303335",
              "completed": False,
              "completion_rate": 0,
              "created_on": "2023-07-27 13:27:25.303335",
              "sub_tasks": [str(ObjectId()), str(ObjectId())],
              "team": str(ObjectId()),
            }
        }
    }