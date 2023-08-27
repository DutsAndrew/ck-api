from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

# StudentNotes should have the following:

# student name
# learning profile (optional)
# teacher notes
# assigned class
# assigned by who


class StudentNote(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    assigned_class: PyObjectId = Field(default_factory=PyObjectId, alias="class_id", required=True)
    assigned_teacher: PyObjectId = Field(default_factory=PyObjectId, alias="teacher_id", required=True)
    learning_profile: Optional[List[str]] = Field(default_factory=list)
    student_name: str = Field(required=True)
    teacher_notes: Optional[List[str]] = Field(default_factory=list)

    model_config= {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "assigned_class": str(ObjectId()),
                "assigned_teacher": str(ObjectId()),
                "learning_profile": ["prefers to sit at back", "likes music", "wants more praise than others"],
                "student_name": "Jacob",
                "teacher_notes": ["parents want to be contacted if he doesn't do homework", "misses school every other Friday for doctor's appointment"],
            }
        }
    }