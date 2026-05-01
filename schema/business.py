from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime

import uuid


class BusinessCreate(BaseModel):
    #BaseModel is the parent class for all schemas
    #This is the model for writing a business to the database
    name: str
    code: str = Field(max_length=5, description="A short abbreviation of the business name")
    #field is what we need to attach extra attributes to the data, in this instance I do not want the user to make a code that is longer than 5 char
    @field_validator("code")
    #field_validator is a function to fix the users input if the validation does not meet on the specifics,
    # in this case if they enter it in the wrong case it can fix it
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        return v.strip().upper()

class BusinessRead(BaseModel):
    #This is the model for reading a business in the database
    #because we are reading trusted data that has already been validated we only need the datatypes for the columns
    id: uuid.UUID
    name: str
    code: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    #configdict is used to convert what is going to be an SQL object to a readable dictionary for pydantic
    # I originally questioned if this should be in the repo or the schema, but even though the repo converts the dict
    # to an object for SQLAlchemy this is considered datashaping and thus belongs in the schema
