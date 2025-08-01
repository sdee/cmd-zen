import asyncio
from db import engine, SessionLocal
from models import Base, Question

SEED_QUESTIONS = [
    {"command": "move cursor left", "shortcut": "h"},
    {"command": "move cursor right", "shortcut": "l"},
    {"command": "move cursor up", "shortcut": "k"},
    {"command": "move cursor down", "shortcut": "j"},
    {"command": "delete character", "shortcut": "x"},
    {"command": "insert mode", "shortcut": "i"},
    {"command": "append after cursor", "shortcut": "a"},
    {"command": "save file", "shortcut": ":w"},
    {"command": "quit", "shortcut": ":q"},
    {"command": "undo", "shortcut": "u"},
]

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        for q in SEED_QUESTIONS:
            exists = await session.execute(
                Question.__table__.select().where(Question.command == q["command"])  # avoid duplicates
            )
            if not exists.first():
                session.add(Question(**q))
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())
