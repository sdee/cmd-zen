# db.py
import os
from sqlalchemy import create_engine

def _build_url_from_rds():
    if os.getenv("RDS_HOSTNAME"):
        user = os.environ["RDS_USERNAME"]
        pwd  = os.environ["RDS_PASSWORD"]
        host = os.environ["RDS_HOSTNAME"]
        port = os.environ.get("RDS_PORT", "5432")
        name = os.environ["RDS_DB_NAME"]
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}"
    return None

def get_engine():
    url = os.getenv("DATABASE_URL") or os.getenv("TEST_DATABASE_URL") or _build_url_from_rds()
    if not url:
        raise RuntimeError("DATABASE_URL or TEST_DATABASE_URL must be set in the environment")
    return create_engine(url, pool_pre_ping=True, future=True)