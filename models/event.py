from pydantic import BaseModel, Field
import uuid

# Events should have the following:

# which calendar they belong to
# which user created it
# any patterns (weekly, daily, monthly, etc)
# color-scheme set by user

class Event(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    calendar: str = Field(required=True)
    created_by: str = Field(required=True)
    patterns = str = Field(default_factory=None, required=True)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537z6e6g1l",
                "calendar": "066de609-b04a-4b30-b46c-32537z6e6g1y",
                "created_by": "066de609-b04a-4b30-b46c-32537z6e6g1i",
                "patterns": None,
            }
        }