from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import Base, engine, SessionLocal
from . import models
from .routes import router
from .config import settings
from .security import hash_password

Base.metadata.create_all(bind=engine)

# Provision the administrator from Render environment variables. The admin
# email cannot be self-registered through the public registration form.
if settings.admin_email and __import__("os").getenv("ADMIN_PASSWORD"):
    with SessionLocal() as db:
        existing = db.query(models.User).filter_by(email=settings.admin_email).first()
        if not existing:
            db.add(models.User(email=settings.admin_email, password_hash=hash_password(__import__("os").environ["ADMIN_PASSWORD"])))
            db.commit()

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
    candidate = (ROOT / path).resolve()
    if candidate.is_file() and ROOT in candidate.parents:
        return FileResponse(candidate)
    return FileResponse(ROOT / "index.html")
