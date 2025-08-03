
import sys
import os
import pytest
import asyncio

import httpx
from httpx import ASGITransport
from asgi_lifespan import LifespanManager

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest



import pytest_asyncio


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_test_db")
class TestQuiz:
    app = None

    async def test_get_quiz(self):
        async with LifespanManager(self.app):
            async with httpx.AsyncClient(base_url="http://test", transport=ASGITransport(app=self.app)) as ac:
                response = await ac.get("/api/quiz")
            assert response.status_code == 200
            assert isinstance(response.json(), list)

    async def test_post_guess(self):
        async with LifespanManager(self.app):
            async with httpx.AsyncClient(base_url="http://test", transport=ASGITransport(app=self.app)) as ac:
                response = await ac.post("/api/guess", json={
                    "question_id": 1,
                    "answer": "h",
                    "is_correct": True
                })
            assert response.status_code == 201
            data = response.json()
            assert data["question_id"] == 1
            assert data["answer"] == "h"
            assert data["is_correct"] is True