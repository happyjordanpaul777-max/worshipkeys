from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import Base, engine
from . import models
from .routes import router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="WorshipKeys API", version="1.0.0")
app.include_router(router)

ROOT = Path(__file__).resolve().parents[1]

@app.get("/api/health")
def health():
    return {"status": "ok", "application": "WorshipKeys"}

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(ROOT / "index.html")

@app.get("/{path:path}", include_in_schema=False)
def spa_fallback(path: str):
    candidate = ROOT / path
    if candidate.is_file() and ROOT in candidate.resolve().parents:
        return FileResponse(candidate)
    return FileResponse(ROOT / "index.html")
