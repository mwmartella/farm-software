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

class BusinessUpdate(BaseModel):
    #This is the model for updating a business in the database
    name: str | None = None
    code: str | None = Field(default=None, max_length=5)
    #The None = None lines added here allow the user to only update 1 of the 2 fields without crashing
    # We still have to keep the max_length constraint on the code otherwise a user could bypass that check by using update

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v: str | None) -> str | None:
        #The type hints have to match the type hints in the model
        if v is not None:
            return v.strip().upper()
        return v
        #We add the second return here because this makes it what is called "explicit"
        # When V is none without it would default to python returning None but that is not best practise.
        # This makes it crystal clear what is meant to happen and does not rely on python getting it right.

    #This is the 3 fields that we want the user to be able to update.
    # name and code can be updated as they are linked to the UUID so they are not used for linked data.
    # We do not include created_at because that should not change on an update
    # We do not include updated_at because that will be filled out by the onupdate=func.now() code in the model