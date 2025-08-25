from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/greet")
def greet():
    return {"message": "Hello from FastAPI!"}

# Mount static files - IMPORTANT: This must come BEFORE the catch-all route
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html for the root path explicitly
@app.get("/")
async def serve_root():
    return FileResponse("static/index.html")

# Catch-all route to serve the frontend for client-side routing
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # First check if it exists as an actual file
    if full_path and os.path.exists(os.path.join("static", full_path)):
        return FileResponse(os.path.join("static", full_path))
    
    # Otherwise return index.html for client-side routing
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    else:
        return {"detail": "Frontend not deployed. Build the React app and copy to static/ directory."}