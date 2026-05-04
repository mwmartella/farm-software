from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from schema.validators import normalise_code_upper

import uuid


class BusinessCreate(BaseModel):
    #BaseModel is the parent class for all schemas
    #This is the model for writing a business to the database
    name: str = Field(min_length=1)
    #we make min length 1 so the user cannot pass an empty '' string, this is different to not None
    code: str = Field(min_length=1, max_length=5, description="A short abbreviation of the business name")
    #field is what we need to attach extra attributes to the data, in this instance I do not want the user to make a code that is longer than 5 char
    abn: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    email: str | None = Field(default=None)
    is_supplier: bool | None = Field(default=False)
    @field_validator("code")
    #field_validator is a function to fix the users input if the validation does not meet on the specifics,
    # in this case if they enter it in the wrong case it can fix it
    @classmethod
    def validate_code(cls, v: str) -> str:
        return normalise_code_upper(v)
    #Even though ive imported a function to do this the @classmethod structure needs a function to run correctly
    # so we still need a validate_code() function and we just have our imported logic inside it preventing copied code

class BusinessRead(BaseModel):
    #This is the model for reading a business in the database
    #because we are reading trusted data that has already been validated we only need the datatypes for the columns
    id: uuid.UUID
    name: str
    code: str
    abn: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    email: str | None = Field(default=None)
    is_supplier: bool | None = Field(default=False)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    #configdict is used to convert what is going to be an SQL object to a readable dictionary for pydantic
    # I originally questioned if this should be in the repo or the schema, but even though the repo converts the dict
    # to an object for SQLAlchemy this is considered datashaping and thus belongs in the schema

class BusinessUpdate(BaseModel):
    #This is the model for updating a business in the database
    name: str | None = Field(default=None, min_length=1)
    code: str | None = Field(default=None, min_length=1, max_length=5)
    abn: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    email: str | None = Field(default=None)
    is_supplier: bool | None = Field(default=None)
    #The None = None lines added here allow the user to only update 1 of the 2 fields without crashing
    # We still have to keep the max_length constraint on the code otherwise a user could bypass that check by using update

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str | None) -> str | None:
        return normalise_code_upper(v)

    #This is the 3 fields that we want the user to be able to update.
    # name and code can be updated as they are linked to the UUID so they are not used for linked data.
    # We do not include created_at because that should not change on an update
    # We do not include updated_at because that will be filled out by the onupdate=func.now() code in the model