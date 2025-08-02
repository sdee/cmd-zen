from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP

Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    command = Column(String, nullable=False)
    shortcut = Column(String, nullable=False)

from sqlalchemy.sql import func

class Guess(Base):
    __tablename__ = "guesses"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, nullable=False)  # Foreign key to Question
    answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
