from datetime import datetime


## Notes should have the following:

# Who created note
# What team note belongs to
# When note was created
# Who has made edits to the notes and what changes did they make
# On what day the note was created
# saved notes should be added to team's calendar
# colorscheme set by group

class Note():
    def __init__(self, db, **kwargs):
        # Model for Note
        self.collection = db['notes']

        self.assigned_team = kwargs.get("assigned_team")
        self.edits = kwargs.get("edits", [])
        self.created_on = kwargs.get("created_on", datetime.now())
        self.note = kwargs.get("note")
        self.who_created = kwargs.get("who_created")

    def to_dict(self):
        return {
            "assigned_team": self.assigned_team,
            "edits": self.edits,
            "created_on": self.created_on,
            "note": self.note,
            "who_created": self.who_created,
        }
    
    async def save(self):
        result = await self.collection.insert_one(self.to_dict())
        return result.inserted_id
    
    @classmethod
    async def find_by_id(cls, db, note_id):
        collection = db['notes'] # use the notes collection
        note_data = await collection.find_one({"_id": note_id})
        if note_data:
            return cls(db, **note_data)
        else:
            return None
    