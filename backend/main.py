
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
import os
import psycopg2
from fastapi.staticfiles import StaticFiles


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    db: str


from fastapi import status
from fastapi.responses import JSONResponse

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
def health_check():
    db_status = "ok"
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"), connect_timeout=2)
        conn.close()    
    except Exception:
        db_status = "error"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "db": db_status},
        )
    return {"status": "ok", "db": db_status}

@app.get("/api/greet")
def greet():
    return {"message": "Hello from FastAPI!"}

# Serve React static files if present
if os.path.isdir("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
