import pytest
from collections import defaultdict
from routers.quiz import calculate_metrics, set_sessionmaker
from models import Question, Guess
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
set_sessionmaker(TestingSessionLocal)

@pytest.mark.parametrize("guesses_with_questions, expected_metrics", [
    (
        [
            (Guess(question_id=1, answer="ls", is_correct=True), Question(id=1, command="ls", shortcut="ls")),
            (Guess(question_id=1, answer="ls", is_correct=True), Question(id=1, command="ls", shortcut="ls")),
            (Guess(question_id=2, answer="cd", is_correct=False), Question(id=2, command="cd", shortcut="cd"))
        ],
        {
            "total_guesses": 3,
            "score": 2 / 3,
            "tally_by_command": {
                "ls": {"correct": 2, "incorrect": 0},
                "cd": {"correct": 0, "incorrect": 1}
            }
        }
    ),
    (
        [],
        {
            "total_guesses": 0,
            "score": 0.0,
            "tally_by_command": {}
        }
    )
])
def test_calculate_metrics(guesses_with_questions, expected_metrics):
    metrics = calculate_metrics(guesses_with_questions)
    assert metrics == expected_metrics
