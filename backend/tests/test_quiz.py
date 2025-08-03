
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # TODO: find a more elegant solution
from main import app
from fastapi.testclient import TestClient

def test_get_quiz():
    with TestClient(app) as client:
        response = client.get("/api/quiz")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
