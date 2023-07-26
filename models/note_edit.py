from datetime import datetime

class NoteEdit:
    def __init__(self, db, **kwargs):
        # Model for NoteEdit
        self.collection = db['noteedits']  # Use the 'noteedits' collection

        self.edited_by = kwargs.get("edited_by")
        self.new_entry = kwargs.get("newEntry")
        self.old_entry = kwargs.get("old_entry")
        self.created_on = kwargs.get("created_on", datetime.now())

    def to_dict(self):
        return {
            "edited_by": self.edited_by,
            "newEntry": self.newEntry,
            "old_entry": self.old_entry,
            "created_on": self.created_on,
        }

    # Save the note edit to the database
    async def save(self):
        result = await self.collection.insert_one(self.to_dict())
        return result.inserted_id

    # Fetch a note edit by its ObjectID
    @classmethod
    async def find_by_id(cls, db, note_edit_id):
        collection = db['noteedits']  # Use the 'noteedits' collection
        note_edit_data = await collection.find_one({"_id": note_edit_id})
        if note_edit_data:
            return cls(db, **note_edit_data)
        return None