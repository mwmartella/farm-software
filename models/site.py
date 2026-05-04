from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Uuid, ForeignKey
from datetime import datetime
from app.base import Base

import uuid

class Sites(Base):
    __tablename__ = "sites"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String(5), unique=True, nullable=False)
    business_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("business.id"), nullable=False)
    #This is how you set up the relationship column, first the name needs to be explict to what it is.
    #Declare the types as normal, and include the ForeignKey with table.column and make not nullable.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Site id={self.id} name={self.name}, code={self.code}>"