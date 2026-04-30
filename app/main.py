from fastapi import FastAPI
from sqlalchemy import text

from app.db import SessionLocal

app = FastAPI(title="Farm Software API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-health")
def database_health_check():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1"))
        return {"database": "ok", "result": result.scalar()}
    finally:
        db.close()