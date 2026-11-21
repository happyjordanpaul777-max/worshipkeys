import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from .database import get_db
from .models import User, UserSession
from .config import settings

_hasher = PasswordHasher()
COOKIE_NAME = "worshipkeys_session"

def hash_password(password: str) -> str:
    return _hasher.hash(password)

def verify_password(password: str, encoded: str) -> bool:
    try:
        return _hasher.verify(encoded, password)
    except (VerifyMismatchError, VerificationError):
        return False

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def create_session(db: Session, user: User) -> str:
    token = secrets.token_urlsafe(40)
    expiry = datetime.now(timezone.utc) + timedelta(days=settings.session_days)
    db.add(UserSession(user_id=user.id, token_hash=hash_token(token), expires_at=expiry))
    db.commit()
    return token

def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in")
    session = db.query(UserSession).filter_by(token_hash=hash_token(token)).first()
    if not session:
        raise HTTPException(status_code=401, detail="Session is invalid or expired")
    expiry = session.expires_at
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if expiry <= datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Account is unavailable")
    return user

def admin_user(user: User = Depends(current_user)) -> User:
    if user.email.lower() != settings.admin_email:
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
