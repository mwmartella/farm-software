from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from schema.validators import normalise_code_upper

import uuid


class SitesCreate(BaseModel):
    name: str = Field(min_length=1)
    code: str = Field(min_length=1, max_length=5, description="A short abbreviation of the site name")
    business_id: uuid.UUID
    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        return normalise_code_upper(v)

class SitesRead(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    business_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SitesUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    code: str | None = Field(default=None, min_length=1, max_length=5)
    business_id: uuid.UUID | None = None #We put this here incase one business takes over that of another.

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str | None) -> str | None:
        return normalise_code_upper(v)