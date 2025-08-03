import os
from dotenv import load_dotenv

import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers import quiz, health
from db import get_engine, get_sessionmaker
import logging

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app(sessionmaker=None):
    if sessionmaker is None:
        engine = get_engine()
        sessionmaker = get_sessionmaker(engine)
    quiz.set_sessionmaker(sessionmaker)
    logger.debug(f"Sessionmaker provided: {sessionmaker}")
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(quiz.router)
    app.include_router(health.router)

    @app.get("/api/greet")
    def greet():
        return {"message": "Hello from FastAPI!"}

    if os.path.isdir("static"):
        app.mount("/", StaticFiles(directory="static", html=True), name="static")
    logger.debug("App initialized successfully")
    return app

# Default app for production
app = create_app()
# Serve React static files if present
if os.path.isdir("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
