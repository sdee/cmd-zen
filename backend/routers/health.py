from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg2
import os

class HealthResponse(BaseModel):
    status: str
    db: str

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    db_status = "ok"
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"), connect_timeout=2)
        conn.close()
    except Exception:
        db_status = "error"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "db": db_status},
        )
    return {"status": "ok", "db": db_status}
