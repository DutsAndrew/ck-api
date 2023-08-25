from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

# Lessons should have the following:

# which class it belongs to
# duration
# optional days-weeks if a unit or multi-day/week lesson
# needed materials
# online website resource list
# standards taught
# activities
# essential question
# teacher is doing section
# students are doing section
# intervention / differentiation notes
# fast finisher notes
# extra notes


class Lesson(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    activities: Optional[List[str]] = Field(default_factory=list)
    assigned_classes: Optional[List[PyObjectId]] = Field(default_factory=list)
    differentiation_notes: Optional[List[str]] = Field(default_factory=list)
    essential_question: Optional[str] = Field(default=str)
    duration: datetime | str = Field(default=str)
    extra_notes: Optional[List[str]] = Field(default_factory=list)
    fast_finisher_notes: Optional[List[str]] = Field(default_factory=list)
    intervention_notes: Optional[List[str]] = Field(default_factory=list)
    name: str = Field(required=True)
    needed_materials: Optional[List[str]] = Field(default_factory=list)
    online_resource_links: Optional[List[str]] = Field(default_factory=list)
    standards_taught: Optional[List[str]] = Field(default_factory=list)
    students_are_doing: Optional[List[str]] = Field(default_factory=list)
    tag: str = Field(default=str)
    teacher_is_doing: Optional[List[str]] = Field(default_factory=list)

    model_config= {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "activities": [str(ObjectId()), str(ObjectId())],
                "assigned_classes": [str(ObjectId()), str(ObjectId())],
                "differentiation_notes": ["Sit ___ away from ___", "___ needs ___ accommodation"],
                "essential_question": "Can I describe what a 5 point summary is?",
                "duration": "60 minutes / 2 weeks / 3 days, etc",
                "extra_notes": ["Setup whiteboards", "sharpen all pencils"],
                "fast_finisher_notes": ["Have students hop onto ___", "read"],
                "intervention_notes": ["small groups for red reading level", "have ___ work with ___"],
                "name": "Water Cycle Lesson",
                "needed_materials": ["pencils", "planner", "chromebook"],
                "online_resource_links": ["google.com", "wikipedia.com"],
                "standards_taught": ["6.1.1 - blah blah blah", "8.5.1 - this that"],
                "students_are_doing": ["working on starter", "getting materials", "finding partner"],
                "tag": "Science",
                "teacher_is_doing": ["taking attendance", "checking seating chart", "passing out materials"],
            }
        }
    }