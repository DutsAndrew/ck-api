# Events should have the following:

# which calendar they belong to
# which user created it
# any patterns (weekly, daily, monthly, etc)
# color-scheme set by user

class Event:
    def __init__(self, db, **kwargs):
        # Model for Event
        self.collection = db['events']  # Use the 'events' collection

        self.calendar = kwargs.get("calendar")
        self.color_scheme = kwargs.get("color_scheme")
        self.created_by = kwargs.get("created_by")
        self.patterns = kwargs.get("patterns", [])

    def to_dict(self):
        return {
            "calendar": self.calendar,
            "color_scheme": self.color_scheme,
            "created_by": self.created_by,
            "patterns": self.patterns,
        }

    # Save the event to the database
    async def save(self):
        result = await self.collection.insert_one(self.to_dict())
        return result.inserted_id

    # Fetch an event by its ObjectID
    @classmethod
    async def find_by_id(cls, db, event_id):
        collection = db['events']  # Use the 'events' collection
        event_data = await collection.find_one({"_id": event_id})
        if event_data:
            return cls(db, **event_data)
        return None