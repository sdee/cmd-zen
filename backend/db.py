# db.py
import os
from typing import Generator, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# ---- build URL from env or EB's RDS_* ----
def _db_url() -> str:
    url = os.getenv("DATABASE_URL") or os.getenv("TEST_DATABASE_URL")
    if url:
        return url
    if os.getenv("RDS_HOSTNAME"):
        return (
            "postgresql+psycopg2://"
            f"{os.environ['RDS_USERNAME']}:{os.environ['RDS_PASSWORD']}"
            f"@{os.environ['RDS_HOSTNAME']}:{os.getenv('RDS_PORT','5432')}"
            f"/{os.environ['RDS_DB_NAME']}"
        )
    raise RuntimeError("Set DATABASE_URL/TEST_DATABASE_URL or provide RDS_* vars.")

_engine = None
_Session = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(_db_url(), pool_pre_ping=True, future=True)
    return _engine

def get_sessionmaker():
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    return _Session

# FastAPI dependency (use if you want)
def get_db() -> Generator[Session, None, None]:
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()