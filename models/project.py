from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ValidationError
from models.bson_object_id import PyObjectId
from bson import ObjectId

## Projects must have the following:
# which team they belong to
# project name
# project deadline
# array of uncompleted tasks
# array of completed tasks
# whether project is completed
# flag if project is overdue
# warning flag when a project is due in less than 7 days

class Project(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    completed: bool = Field(default_factory=False)
    completed_tasks: Optional[List[PyObjectId]] = Field(default_factory=list)
    deadline: datetime = Field(required=True)
    name: str = Field(required=True)
    uncompleted_tasks: Optional[List[PyObjectId]] = Field(default_factory=list)

    @property
    def behind_schedule(self):
        return datetime.now() > self.deadline
    
    @property
    def deadline_approaching(self):
        return (self.deadline - datetime.now()) < timedelta(days=7)
    
    @field_validator('name')
    @classmethod
    def validate_project_name(cls, v):
        if not v:
            raise ValidationError('Your project must have a name')
        if len(v) < 1:
            raise ValidationError('You did not add a project name')
        if len(v) > 1000:
            raise ValidationError('Your project name is longer than 1000 characters')
        return v
    
    @field_validator('deadline')
    @classmethod
    def validate_deadline(cls, v):
        if v < datetime.now() + timedelta(minutes=30):
            raise ValidationError('Your deadline submission must be at least 30 minutes')

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
              "completed": False,
              "completed_tasks": [str(ObjectId()), str(ObjectId())],
              "deadline": "2023-07-27 13:27:25.303335",
              "name": "Build the Eiffel Tower",
              "uncompleted_tasks": [str(ObjectId()), str(ObjectId())],
            }
        }
    }