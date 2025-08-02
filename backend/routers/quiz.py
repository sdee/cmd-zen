from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from db import SessionLocal
from models import Question
from typing import List
from pydantic import BaseModel

class QuestionOut(BaseModel):
    id: int
    command: str
    shortcut: str
    class Config:
        orm_mode = True

async def get_db():
    async with SessionLocal() as session:
        yield session

router = APIRouter()

@router.get("/api/quiz", response_model=List[QuestionOut])
async def get_quiz(db=Depends(get_db)):
    result = await db.execute(select(Question))
    questions = result.scalars().all()
    return questions
