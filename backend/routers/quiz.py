from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Counter
import logging

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        logger.debug("Session accessed in get_db")
        logger.debug(f"Session state: {session}")
        yield session


def set_sessionmaker(sm):
    global SessionLocal
    SessionLocal = sm

# Log the state of SessionLocal
logger.debug(f"SessionLocal state: {SessionLocal}")

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


@router.get("/api/guesses", response_model=List[GuessOut])
async def get_guesses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Guess))
    guesses = result.scalars().all()
    guesses.sort(key=lambda g: g.timestamp, reverse=True)
    return guesses


# Extract tallying logic into a separate function
def calculate_metrics(guesses_with_questions):
    tally_by_command = defaultdict(lambda: {"correct": 0, "incorrect": 0})
    for guess, question in guesses_with_questions:
        command = question.command
        if guess.is_correct:
            tally_by_command[command]["correct"] += 1
        else:
            tally_by_command[command]["incorrect"] += 1

    total_guesses = len(guesses_with_questions)
    correct_guesses_count = sum(guess.is_correct for guess, _ in guesses_with_questions)
    score = correct_guesses_count / total_guesses if total_guesses > 0 else 0.0

    return {
        "total_guesses": total_guesses,
        "score": score,
        "tally_by_command": dict(tally_by_command)
    }

# Refactor get_metrics to use the new function
@router.get("/api/metrics", response_model=dict)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    logger.debug("Session accessed in get_db")
    logger.debug(f"Session state: {db}")

    result = await db.execute(
        select(Guess, Question).join(Question, Guess.question_id == Question.id)
    )
    guesses_with_questions = result.all()

    logger.debug("Fetching metrics data")
    logger.debug(f"Guesses with questions: {guesses_with_questions}")

    metrics = calculate_metrics(guesses_with_questions)

    logger.debug(f"Metrics calculated: {metrics}")
    return metrics

logger.debug("Router setup completed")