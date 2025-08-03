
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable

# SessionLocal will be injected via dependency
SessionLocal = None
from models import Question, Guess
from typing import List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class QuestionOut(BaseModel):
    id: int
    command: str
    shortcut: str
    model_config = ConfigDict(from_attributes=True)

class GuessCreate(BaseModel):
    question_id: int
    answer: str
    is_correct: bool

class GuessOut(BaseModel):
    id: int
    question_id: int
    answer: str
    is_correct: bool
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)



async def get_db():
    assert SessionLocal is not None, "SessionLocal must be set before using get_db"
    async with SessionLocal() as session:
        yield session


def set_sessionmaker(sm):
    global SessionLocal
    SessionLocal = sm

router = APIRouter()


@router.get("/api/quiz", response_model=List[QuestionOut])
async def get_quiz(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question))
    questions = result.scalars().all()
    return questions


@router.post("/api/guess", response_model=GuessOut, status_code=status.HTTP_201_CREATED)
async def create_guess(guess: GuessCreate, db: AsyncSession = Depends(get_db)):
    new_guess = Guess(
        question_id=guess.question_id,
        answer=guess.answer,
        is_correct=guess.is_correct
    )
    db.add(new_guess)
    await db.commit()
    await db.refresh(new_guess)
    return new_guess


