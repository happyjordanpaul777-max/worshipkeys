import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
# Load a private .env file for local laptop installations. Render environment
# variables continue to take precedence over values in this file.
load_dotenv(ROOT / ".env", override=False)

class Settings:
    app_name = os.getenv("APP_NAME", "WorshipKeys")
    secret_key = os.getenv("SECRET_KEY", "change-this-before-deploying-worshipkeys")
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'worshipkeys.db'}")
    admin_email = os.getenv("ADMIN_EMAIL", "happyjordanpaul777@gmail.com").strip().lower()
    session_days = int(os.getenv("SESSION_DAYS", "14"))
    # Local HTTP uses an insecure cookie; set COOKIE_SECURE=true behind HTTPS.
    cookie_secure = os.getenv("COOKIE_SECURE", "false").lower() in ("1", "true", "yes")
    public_base_url = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

settings = Settings()
