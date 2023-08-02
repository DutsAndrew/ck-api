from bson import ObjectId

# FastAPI encodes and decodes data as JSON, MongoDB stores data as BSON,
# and BSON can store some values as non-JSON like as ObjectId, so that's what we are doing here

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema