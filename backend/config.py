import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)

class Settings:
    app_name = os.getenv("APP_NAME", "WorshipKeys")
    secret_key = os.getenv("SECRET_KEY", "local-worshipkeys-only")
    local_shared_mode = os.getenv("LOCAL_SHARED_MODE", "true").lower() in ("1", "true", "yes")
    # Local songbook mode always uses laptop-local SQLite. Old Render URLs in .env are ignored.
    database_url = (
        os.getenv("LOCAL_DATABASE_URL", f"sqlite:///{ROOT / 'worshipkeys.db'}")
        if local_shared_mode
        else os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'worshipkeys.db'}")
    )
    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    session_days = int(os.getenv("SESSION_DAYS", "14"))
    cookie_secure = os.getenv("COOKIE_SECURE", "false").lower() in ("1", "true", "yes")
    public_base_url = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

settings = Settings()