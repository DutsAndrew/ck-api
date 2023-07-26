import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCollection, ListField, DateTimeField, BooleanField, ReferenceField
from datetime import datetime

## Sub tasks should have the following:

# task it is assigned to
# completion status (yes/no)
# when subtask was created
# when subtask was completed
# users assigned to sub task

class SubTask:
    def __init__(self, db, **kwargs):
        # Model for SubTask
        self.collection = db['subtasks']  # Use the 'subtasks' collection

        self.assigned_to = kwargs.get("assigned_to", [])
        self.completed = kwargs.get("completed", False)
        self.completed_on = kwargs.get("completed_on")
        self.created_on = kwargs.get("created_on", datetime.now())
        self.task = kwargs.get("task")

    def to_dict(self):
        return {
            "assigned_to": self.assigned_to,
            "completed": self.completed,
            "completed_on": self.completed_on,
            "created_on": self.created_on,
            "task": self.task,
        }

    # Save the subtask to the database
    async def save(self):
        result = await self.collection.insert_one(self.to_dict())
        return result.inserted_id

    # Fetch a subtask by its ObjectID
    @classmethod
    async def find_by_id(cls, db, subtask_id):
        collection = db['subtasks']  # Use the 'subtasks' collection
        subtask_data = await collection.find_one({"_id": subtask_id})
        if subtask_data:
            return cls(db, **subtask_data)
        return None