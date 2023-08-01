from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId

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
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    approved_edits: Optional[List[ObjectId]] = Field(None)
    assigned_team: Optional[PyObjectId] = Field(None)
    assigned_user: Optional[PyObjectId] = Field(None)
    created_by: Optional[PyObjectId] = Field(None)
    created_on: datetime = Field(default_factory=lambda: datetime.now)
    edits: Optional[List[PyObjectId]] = Field(default_factory=list)
    note: str = Field(required=True)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "approved_edits": [str(ObjectId()), str(ObjectId())],
                "assigned_team": str(ObjectId()),
                "assigned_user": None,
                "created_by": str(ObjectId()),
                "created_on": "2023-07-27 13:27:25.303335",
                "edits": [str(ObjectId()), str(ObjectId())],
                "note": "<h1>6th Team Meeting</h1><br><p>We talked about nothing</p>",
            }
        }
    }