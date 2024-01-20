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

    def to_dict(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'job_title': self.job_title,
            'company': self.company,
            'user_id': self.user_id
        }

class Team(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    calendar: str = Field(default_factory=str)
    description: str
    name: str
    notes: List[str] = Field(default_factory=list)
    notifications: List[str] = Field(default_factory=list)
    tasks: List[str] = Field(default_factory=list)
    team_color: str
    team_lead: None | UserRef = Field(default_factory=None)
    users: List[UserRef] = Field(default_factory=list)
    pending_users: List[UserRef] = Field(default_factory=list)

    def add_team_calendar(self, calendar_id: str):
        self.calendar = calendar_id

    def encode_team_for_upload(self):
        users_dicts = [user.to_dict() for user in self.users]
        pending_users_dicts = [user.to_dict() for user in self.pending_users]

        # convert team lead if present
        team_lead_dict = self.team_lead.to_dict() if self.team_lead else None

        return {
            'id': self.id,
            'calendar': self.calendar,
            'description': self.description,
            'name': self.name,
            'notes': self.notes,
            'notifications': self.notifications,
            'tasks': self.tasks,
            'team_color': self.team_color,
            'team_lead': team_lead_dict,
            'users': users_dicts,
            'pending_users': pending_users_dicts
        }

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str,
            PyObjectId: str,
          },
    }