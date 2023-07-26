from datetime import datetime

class User:
    def __init__(self, db, **kwargs):
        # Model for User
        self.collection = db['users']  # Use the 'users' collection

        self.email = kwargs.get("email")
        self.account_type = kwargs.get("account_type", "basic")
        self.calendars = kwargs.get("calendars", [])
        self.company = kwargs.get("company", None)
        self.tasks = kwargs.get("tasks", [])
        self.teams = kwargs.get("teams", [])
        self.joined = kwargs.get("joined", datetime.now())
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.last_online = kwargs.get("last_online", datetime.now())
        self.job_title = kwargs.get("job_title", None)

    # Helper method to convert User object to a dictionary
    def to_dict(self):
        return {
            "email": self.email,
            "account_type": self.account_type,
            "calendars": self.calendars,
            "company": self.company,
            "tasks": self.tasks,
            "teams": self.teams,
            "joined": self.joined,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "last_online": self.last_online,
            "job_title": self.job_title,
        }
    
    # Save the user to the database
    async def save(self):
        result = await self.collection.insert_one(self.to_dict())
        return result.inserted_id

    # Fetch a user by email
    @classmethod
    async def find_by_email(cls, db, email):
        collection = db['users'] # use the users collection
        user_data = await collection.find_one({"email": email})
        if user_data:
            return cls(**user_data)
        return None