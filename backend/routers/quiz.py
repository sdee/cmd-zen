from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
import logging
from db import get_db  # Import the centralized get_db function
from models import Question, Guess
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for responses
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

# Endpoint to fetch quiz questions
@router.get("/api/quiz", response_model=List[QuestionOut])
def get_quiz(db: Session = Depends(get_db)):
    result = db.execute(select(Question))
    questions = result.scalars().all()
    return questions

# Endpoint to create a new guess
@router.post("/api/guess", response_model=GuessOut, status_code=status.HTTP_201_CREATED)
def create_guess(guess: GuessCreate, db: Session = Depends(get_db)):
    new_guess = Guess(
        question_id=guess.question_id,
        answer=guess.answer,
        is_correct=guess.is_correct
    )
    db.add(new_guess)
    db.commit()
    db.refresh(new_guess)
    return new_guess

# Endpoint to fetch all guesses
@router.get("/api/guesses", response_model=List[GuessOut])
def get_guesses(db: Session = Depends(get_db)):
    result = db.execute(select(Guess))
    guesses = result.scalars().all()
    guesses.sort(key=lambda g: g.timestamp, reverse=True)
    return guesses

# Function to calculate metrics
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

# Endpoint to fetch metrics
@router.get("/api/metrics", response_model=dict)
def get_metrics(db: Session = Depends(get_db)):
    logger.debug("Session accessed in get_db")
    logger.debug(f"Session state: {db}")

    result = db.execute(
        select(Guess, Question).join(Question, Guess.question_id == Question.id)
    )
    guesses_with_questions = result.all()

    logger.debug("Fetching metrics data")
    logger.debug(f"Guesses with questions: {guesses_with_questions}")

    metrics = calculate_metrics(guesses_with_questions)

    logger.debug(f"Metrics calculated: {metrics}")
    return metrics

logger.debug("Router setup completed")