from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

# Announcements should have the following:
## when it was created
## what text it needs to send
## how long to display for

class Announcement(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    announcement: str = Field(required=True)
    created_on: datetime = Field(default_factory=lambda: datetime.now(), required=True)
    display_for: timedelta = Field(default_factory=lambda: timedelta(weeks=2), required=True)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "announcement": "This is a new feature, enjoy!",
                "created_on": "2023-07-27 13:27:25.303335",
                "display_for": "2w",
            }
        }