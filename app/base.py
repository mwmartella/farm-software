from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass #left blank because Declarative base that we imported above contains all the AQL machinery that alembic needs