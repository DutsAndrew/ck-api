from datetime import datetime
from pydantic import BaseModel, Field
import uuid

class NoteEdit(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    created_on: datetime = Field(default_factory=lambda: datetime.now(), required=True)
    edited_by: str = Field(required=True)
    new_entry: str = Field(required=True)
    old_entry: str = Field(required=True)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "123abcd-b04a-4b30-b46c-32537c7f1f6e",
                "created_on": "2023-07-27 13:27:25.303335",
                "edited_by": "123adef-b04a-4b30-b46c-32537c7f1f6e",
                "new_entry": "<p>This actually happened</p>",
                "old_entry": "<p>This did not happen</p>",
            }
        }