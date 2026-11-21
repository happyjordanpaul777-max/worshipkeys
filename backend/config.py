import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Settings:
    app_name = os.getenv("APP_NAME", "WorshipKeys")
    secret_key = os.getenv("SECRET_KEY", "change-this-before-deploying-worshipkeys")
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'worshipkeys.db'}")
    admin_email = os.getenv("ADMIN_EMAIL", "happyjordanpaul777@gmail.com").strip().lower()
    session_days = int(os.getenv("SESSION_DAYS", "14"))
    cookie_secure = os.getenv("COOKIE_SECURE", "true").lower() in ("1", "true", "yes")
    public_base_url = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

settings = Settings()
