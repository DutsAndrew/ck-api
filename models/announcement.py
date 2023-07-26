from datetime import datetime

# Announcements should have the following:
## when it was created
## what text it needs to send
## how long to display for

class Announcement:
    def __init__(self, db, **kwargs):
        # Model for Announcement
        self.collection = db['announcements']  # Use the 'announcements' collection

        self.announcement = kwargs.get("announcement")
        self.created_on = kwargs.get("created_on", datetime.now())
        self.display_for = kwargs.get("display_for")

    def to_dict(self):
        return {
            "announcement": self.announcement,
            "created_on": self.created_on,
            "display_for": self.display_for,
        }

    # Save the announcement to the database
    async def save(self):
        result = await self.collection.insert_one(self.to_dict())
        return result.inserted_id

    # Fetch an announcement by its ObjectID
    @classmethod
    async def find_by_id(cls, db, announcement_id):
        collection = db['announcements']  # Use the 'announcements' collection
        announcement_data = await collection.find_one({"_id": announcement_id})
        if announcement_data:
            return cls(db, **announcement_data)
        return None
