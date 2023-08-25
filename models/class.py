from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId
from typing import Optional, List

# Classes should have the following:

# course name
# taught by who array (multiple teachers allowed)
# students enrolled
# lessons array
# student notes array
# student seating chart
# class period or time block entry
# class description
# class length / duration
# grade level or course level

class Class(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    course_block: str = Field(required=True) # class period or block
    course_length: Optional[str] = Field(default=str)
    course_level: str = Field(required=True) # grade level or course level
    course_name: str = Field(required=True)
    description: Optional[str] = Field(default=str)
    lessons: Optional[List[PyObjectId]] = Field(default_factory=list)
    student_count: int = Field(default_factory=0)
    student_notes: Optional[List[PyObjectId]] = Field(default_factory=list)

    model_config= {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "course_block": "1AB",
                "course_length": "4 Months / 1 Semester / 2 Quarters, etc",
                "course_level": "1010 / 8th Grade / Kindergarten / 3060, etc",
                "course_name": "Integrated Mathematics",
                "description": "Elementary level reading for students 1-2 years below grade level",
                "lessons": [str(ObjectId()), str(ObjectId())],
                "student_count": 150,
                "student_notes": [str(ObjectId()), str(ObjectId())],
            }
        }
    }