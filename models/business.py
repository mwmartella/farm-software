#models/business.py
#have commented up this first model just so when I write more of them I can understand and remember why I did things.
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Uuid, Boolean
from datetime import datetime

import uuid

from app.base import Base
#imported from the base.py file, this class tells python that this is a database table and to treat it as such,
# without this python would think this is just a normal object

class Business(Base):
    __tablename__ = "business"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String(5), unique=True, nullable=False)
    abn: Mapped[str] = mapped_column(String, nullable=True)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    is_supplier: Mapped[bool] = mapped_column(Boolean, server_default='false', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    #sever_default means a TS will be created on row creation
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    #onupdate + server_default together mean on row creation and on the row getting an "UPDATE" statement the time stamps will update accordingly

    def __repr__(self) -> str:
        return f"<Business id={self.id} name={self.name}, code={self.code}>"
    #this is here just as a debugger tool, if i needed to print the object it would come in code I could not read
    #this just prints out the info inside the object so I can see it if needed.

# AFTER THIS IS DONE - edit the __init__.py file!
