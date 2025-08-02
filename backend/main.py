
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers import quiz, health

app = FastAPI()
# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(quiz.router)
app.include_router(health.router)


@app.get("/api/greet")
def greet():
    return {"message": "Hello from FastAPI!"}

# Serve React static files if present
if os.path.isdir("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
