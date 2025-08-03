
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from db import get_engine, get_sessionmaker
from main import create_app
from routers import quiz
from dotenv import load_dotenv
load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/cmdzen_test")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


import pytest_asyncio

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db(request):
    # Create engine and sessionmaker inside the fixture/event loop
    engine = get_engine(TEST_DATABASE_URL, echo=False)
    TestSessionLocal = get_sessionmaker(engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


    # Provide the app with the test sessionmaker for the test class
    request.cls.app = create_app(TestSessionLocal)

    yield
    await engine.dispose()
