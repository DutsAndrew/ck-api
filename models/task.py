from datetime import datetime

# Tasks should have the following:

## what team if any it belongs to
## which user(s) it is currently assigned to
## what time it was created
## what time it needs to be completed
## what time it was completed
## status of completion
## array of sub-tasks if chosen
## color_scheme set by group

class Task:
    def __init__(self, db, **kwargs):
        # Model for Task
        self.collection = db['tasks']  # Use the 'tasks' collection

        self.assigned_to = kwargs.get("assigned_to", [])
        self.color_scheme = kwargs.get("color_scheme")
        self.complete_by = kwargs.get("complete_by")
        self.completed_on = kwargs.get("completed_on")
        self.completed = kwargs.get("completed", False)
        self.created_on = kwargs.get("created_on", datetime.now())
        self.team = kwargs.get("team")

    def to_dict(self):
        return {
            "assigned_to": self.assigned_to,
            "color_scheme": self.color_scheme,
            "complete_by": self.complete_by,
            "completed_on": self.completed_on,
            "completed": self.completed,
            "created_on": self.created_on,
            "team": self.team,
        }

    # Save the task to the database
    async def save(self):
        result = await self.collection.insert_one(self.to_dict())
        return result.inserted_id

    # Fetch a task by its ObjectID
    @classmethod
    async def find_by_id(cls, db, task_id):
        collection = db['tasks']  # Use the 'tasks' collection
        task_data = await collection.find_one({"_id": task_id})
        if task_data:
            return cls(db, **task_data)
        return None