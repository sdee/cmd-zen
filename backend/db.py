

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from models import Base, Question

def get_engine(database_url=None, echo=True):
    if database_url is None:
        database_url = os.getenv("DATABASE_URL") or os.getenv("TEST_DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL or TEST_DATABASE_URL must be set in the environment")
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    return create_async_engine(database_url, echo=echo, future=True)

def get_sessionmaker(engine):
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# No global SessionLocal here! It will be set in main.py and injected in routers.



