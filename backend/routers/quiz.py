
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import SessionLocal
from models import Question, Guess
from typing import List
from pydantic import BaseModel

class QuestionOut(BaseModel):
    id: int
    command: str
    shortcut: str
    class Config:
        orm_mode = True

class GuessCreate(BaseModel):
    question_id: int
    answer: str
    is_correct: bool


from datetime import datetime

class GuessOut(BaseModel):
    id: int
    question_id: int
    answer: str
    is_correct: bool
    timestamp: datetime
    class Config:
        orm_mode = True

async def get_db():
    async with SessionLocal() as session:
        yield session

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


