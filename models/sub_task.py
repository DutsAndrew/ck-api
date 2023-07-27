from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid

## Sub tasks should have the following:

# task it is assigned to
# completion status (yes/no)
# when subtask was created
# when subtask was completed
# users assigned to sub task

class SubTask(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    assigned_to: str = Field(default_factory=None, required=True)
    accompanied_task: str = Field(required=True)
    completed: bool = Field(default_factory=False, required=True)
    completed_on: Optional[datetime] = Field(default=None)
    created_on: datetime = Field(default_factory=lambda: datetime.now(), required=True)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-1a29-c57d-32537c7f1f6e",
                "assigned_to": "066de123-b04a-1a29-c57d-32537c7f1f6e",
                "accompanied_task": "066de153-b04a-1a29-c57d-32537c7f1f6e",
                "completed": False,
                "completed_on": None,
                "created_on": "2023-07-27 13:27:25.303335",
            }
        }