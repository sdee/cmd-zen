from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from routers.quiz import router as quiz_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers under the `/api/` prefix
app.include_router(quiz_router, prefix="/api/quiz", tags=["Quiz"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/greet")
def greet():
    return {"message": "Hello from FastAPI!"}

# Mount static files BEFORE catch-all
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/debug-static")
def debug_static():
    path = os.path.abspath("static")
    files = []
    if os.path.isdir(path):
        for root, _, filenames in os.walk(path):
            for f in filenames:
                rel = os.path.relpath(os.path.join(root, f), path)
                files.append(rel)
    return {"static_path": path, "exists": os.path.isdir(path), "files": files}

@app.get("/")
def serve_index():
    index = os.path.join("static", "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return JSONResponse({"detail": "Frontend not deployed. Build and copy to static/."})

@app.get("/{full_path:path}")
def catch_all(full_path: str):
    # Exclude API paths from being handled by the catch-all route
    if full_path.startswith("api") or full_path.startswith("health") or full_path.startswith("quiz"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    candidate = os.path.join("static", full_path)
    if os.path.exists(candidate) and not os.path.isdir(candidate):
        return FileResponse(candidate)
    index = os.path.join("static", "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return JSONResponse({"detail": "Frontend not deployed. Build and copy to static/."})