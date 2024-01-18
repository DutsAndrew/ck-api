from typing import List, Optional
from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId

# To keep data clean, teams need to hold the majority of the data to keep user data low
## Teams should have the following:

### all tasks that belong to this team
### one calendar per team, no more
### all notes that belong to this team
### all user_id refs of users in this team
### team lead assigned to manage team
### color scheme set by group

class UserRef(BaseModel):
    first_name: str
    last_name: str
    job_title: str
    company: str
    user_id: str = Field(default_factory=str)

class Team(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    calendar: Optional[PyObjectId] = Field(None)
    description: str
    name: str
    notes: Optional[List[PyObjectId]] = Field(default_factory=list)
    notifications: Optional[List[PyObjectId]] = Field(None)
    tasks: Optional[List[PyObjectId]] = Field(default_factory=list)
    team_color: str
    team_lead: Optional[PyObjectId] = Field(None)
    users: Optional[List[UserRef]] = Field(default_factory=list)
    pending_users: Optional[List[UserRef]] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "calendar": str(ObjectId()),
                "notes": [str(ObjectId()), str(ObjectId())],
                "notifications": [str(ObjectId()), str(ObjectId()), str(ObjectId()), str(ObjectId()), str(ObjectId())],
                "tasks": [str(ObjectId()), str(ObjectId())],
                "team_lead": str(ObjectId()),
                "users": [str(ObjectId()), str(ObjectId())],
                "pending_users": [str(ObjectId()), str(ObjectId()), str(ObjectId())]
            }
        }
    }