import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
#if env var not set this will flag a value error so we had to catch it.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    #this function provides a database connection per request and auto cleans up after request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()