from fastapi import FastAPI
from sqlalchemy import text

from app.db import SessionLocal

from app.api.business_routes import router as business_router

app = FastAPI(title="Farm Software API")

app.include_router(business_router)

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

