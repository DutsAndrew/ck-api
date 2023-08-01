from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId

## Sub tasks should have the following:

# task it is assigned to
# completion status (yes/no)
# when subtask was created
# when subtask was completed
# users assigned to sub task

class SubTask(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    assigned_to: Optional[PyObjectId] = Field(None)
    accompanied_task: Optional[PyObjectId] = Field(None)
    completed: bool = Field(default_factory=False)
    completed_on: Optional[datetime] = Field(default=None)
    created_on: datetime = Field(default_factory=lambda: datetime.now)
    sub_task: str = Field(required=True)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "assigned_to": str(ObjectId()),
                "accompanied_task": str(ObjectId()),
                "completed": False,
                "completed_on": None,
                "created_on": "2023-07-27 13:27:25.303335",
                "sub_task": "Buy materials"
            }
        }
    }