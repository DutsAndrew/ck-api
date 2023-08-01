from datetime import datetime
from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId
from typing import Optional

class NoteEdit(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    accepted: bool = Field(False)
    created_on: datetime = Field(default_factory=lambda: datetime.now, required=True)
    edited_by: Optional[PyObjectId] = Field(required=True)
    new_entry: str = Field(required=True)
    old_entry: str = Field(required=True)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "accepted": False,
                "created_on": "2023-07-27 13:27:25.303335",
                "edited_by": str(ObjectId()),
                "new_entry": "<p>This actually happened</p>",
                "old_entry": "<p>This did not happen</p>",
            }
        }
    }