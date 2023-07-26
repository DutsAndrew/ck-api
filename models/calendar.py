## Calendars should have the following:
# what team or user the calendar belongs to
# what events have been created and added to calendar
# what year the calendar is for
# color scheme set by user

class Calendar:
    def __init__(self, db, **kwargs):
        # Model for Calendar
        self.collection = db['calendars']  # Use the 'calendars' collection

        self.color_scheme = kwargs.get("color_scheme")
        self.events = kwargs.get("events", [])
        self.team = kwargs.get("team")
        self.user = kwargs.get("user")
        self.year = kwargs.get("year")

    def to_dict(self):
        return {
            "color_scheme": self.color_scheme,
            "events": [event.to_dict() for event in self.events],
            "team": self.team,
            "user": self.user,
            "year": self.year,
        }

    # Save the calendar to the database
    async def save(self):
        result = await self.collection.insert_one(self.to_dict())
        return result.inserted_id

    # Fetch a calendar by its ObjectID
    @classmethod
    async def find_by_id(cls, db, calendar_id):
        collection = db['calendars']  # Use the 'calendars' collection
        calendar_data = await collection.find_one({"_id": calendar_id})
        if calendar_data:
            return cls(db, **calendar_data)
        return None