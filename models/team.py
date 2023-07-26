import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCollection, StringField, ListField, ReferenceField
from datetime import datetime
from note import Note
from task import Task
from user import User

# To keep data clean, teams need to hold the majority of the data to keep user data low
## Teams should have the following:

### all tasks that belong to this team
### one calendar per team, no more
### all notes that belong to this team
### all user_id refs of users in this team
### team lead assigned to manage team
### color scheme set by group

class Team:
    def __init__(self, db, **kwargs):
        # Model for Team
        self.collection = db['teams']  # Use the 'teams' collection

        self.calendar = kwargs.get("calendar")
        self.color_scheme = kwargs.get("color_scheme")
        self.notes = kwargs.get("notes", [])
        self.tasks = kwargs.get("tasks", [])
        self.team_lead = kwargs.get("team_lead")
        self.users = kwargs.get("users", [])

    def to_dict(self):
        return {
            "calendar": self.calendar,
            "color_scheme": self.color_scheme,
            "notes": [note.to_dict() for note in self.notes],
            "tasks": [task.to_dict() for task in self.tasks],
            "team_lead": self.team_lead,
            "users": self.users,
        }

    # Save the team to the database
    async def save(self):
        result = await self.collection.insert_one(self.to_dict())
        return result.inserted_id

    # Fetch a team by team_lead
    @classmethod
    async def find_by_team_lead(cls, db, team_lead):
        collection = db['teams']  # Use the 'teams' collection
        team_data = await collection.find_one({"team_lead": team_lead})
        if team_data:
            return cls(db, **team_data)
        return None