from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from .database import get_db
from .models import User, UserSession, Song, Idea, IdeaComment, IdeaLike
from .security import hash_password, verify_password, create_session, current_user, admin_user, hash_token, COOKIE_NAME
from .config import settings

router = APIRouter()

class AuthInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

class SongInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    song_key: str = Field(default="", max_length=20)
    transpose: int = Field(default=0)
    tempo_feel: str = Field(default="Medium", max_length=40)
    bpm: int | None = Field(default=None, ge=30, le=300)
    beat: str = Field(default="", max_length=20)
    accompaniment_style: str = Field(default="", max_length=100)
    category: str = Field(default="", max_length=100)
    lyrics: str = Field(min_length=1, max_length=30000)
    notes: str = Field(default="", max_length=3000)

class TextInput(BaseModel):
    content: str = Field(min_length=1, max_length=2000)

def set_cookie(response: Response, token: str):
    response.set_cookie(COOKIE_NAME, token, httponly=True, secure=settings.cookie_secure,
                        samesite="lax", max_age=settings.session_days * 86400, path="/")

def user_payload(user: User):
    return {"id": user.id, "email": user.email, "is_admin": user.email.lower() == settings.admin_email}

def song_payload(s: Song):
    return {"id":s.id,"title":s.title,"song_key":s.song_key,"transpose":s.transpose,
            "tempo_feel":s.tempo_feel,"bpm":s.bpm,"beat":s.beat,"accompaniment_style":s.accompaniment_style,
            "category":s.category,"lyrics":s.lyrics,"notes":s.notes}

@router.post("/api/auth/register", status_code=201)
def register(data: AuthInput, response: Response, db: Session = Depends(get_db)):
    email = str(data.email).strip().lower()
    if email == settings.admin_email:
        raise HTTPException(403, "The administrator account is provisioned securely by the site owner. Please sign in.")
    if db.query(User).filter_by(email=email).first():
        raise HTTPException(409, "An account with this email already exists.")
    user = User(email=email, password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "An account with this email already exists.")
    db.refresh(user)
    set_cookie(response, create_session(db, user))
    return user_payload(user)

@router.post("/api/auth/login")
def login(data: AuthInput, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=str(data.email).strip().lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Email or password is incorrect.")
    set_cookie(response, create_session(db, user))
    return user_payload(user)

@router.post("/api/auth/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        session = db.query(UserSession).filter_by(token_hash=hash_token(token)).first()
        if session:
            db.delete(session)
            db.commit()
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, samesite="lax")
    return {"ok": True}

@router.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return user_payload(user)

@router.get("/api/songs")
def list_songs(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return [song_payload(s) for s in db.query(Song).order_by(Song.title.asc()).all()]

@router.post("/api/songs", status_code=201)
def create_song(data: SongInput, db: Session = Depends(get_db), user: User = Depends(admin_user)):
    song = Song(**data.model_dump())
    db.add(song)
    db.commit()
    db.refresh(song)
    return song_payload(song)

@router.put("/api/songs/{song_id}")
def update_song(song_id: int, data: SongInput, db: Session = Depends(get_db), user: User = Depends(admin_user)):
    song = db.get(Song, song_id)
    if not song:
        raise HTTPException(404, "Song not found.")
    for key, value in data.model_dump().items():
        setattr(song, key, value)
    db.commit()
    db.refresh(song)
    return song_payload(song)

@router.delete("/api/songs/{song_id}")
def delete_song(song_id: int, db: Session = Depends(get_db), user: User = Depends(admin_user)):
    song = db.get(Song, song_id)
    if not song:
        raise HTTPException(404, "Song not found.")
    db.delete(song)
    db.commit()
    return {"ok": True}

def idea_payload(idea: Idea, db: Session, user_id: int):
    owner = db.get(User, idea.user_id)
    comments = db.query(IdeaComment).filter_by(idea_id=idea.id).order_by(IdeaComment.created_at.asc()).all()
    likes = db.query(IdeaLike).filter_by(idea_id=idea.id).count()
    liked = db.query(IdeaLike).filter_by(idea_id=idea.id, user_id=user_id).first() is not None
    return {"id":idea.id,"content":idea.content,"email":owner.email if owner else "Member",
            "created_at":idea.created_at.isoformat(),"likes":likes,"liked":liked,
            "comments":[{"id":c.id,"content":c.content,"email":(db.get(User,c.user_id).email if db.get(User,c.user_id) else "Member"),"created_at":c.created_at.isoformat()} for c in comments]}

@router.get("/api/ideas")
def list_ideas(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(Idea).order_by(Idea.created_at.desc()).limit(200).all()
    return [idea_payload(i, db, user.id) for i in rows]

@router.post("/api/ideas", status_code=201)
def create_idea(data: TextInput, db: Session = Depends(get_db), user: User = Depends(current_user)):
    idea = Idea(user_id=user.id, content=data.content.strip())
    if not idea.content:
        raise HTTPException(422, "Write an idea before posting.")
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea_payload(idea, db, user.id)

@router.post("/api/ideas/{idea_id}/comments", status_code=201)
def add_comment(idea_id: int, data: TextInput, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not db.get(Idea, idea_id):
        raise HTTPException(404, "Idea not found.")
    comment = IdeaComment(idea_id=idea_id, user_id=user.id, content=data.content.strip())
    if not comment.content:
        raise HTTPException(422, "Write a comment first.")
    db.add(comment)
    db.commit()
    return {"ok": True}

@router.post("/api/ideas/{idea_id}/like")
def toggle_like(idea_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not db.get(Idea, idea_id):
        raise HTTPException(404, "Idea not found.")
    existing = db.query(IdeaLike).filter_by(idea_id=idea_id, user_id=user.id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"liked": False}
    db.add(IdeaLike(idea_id=idea_id, user_id=user.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
    return {"liked": True}

# Private local-laptop songbook API. This is deliberately disabled on Render
# unless LOCAL_SHARED_MODE=true, and additionally accepts loopback clients only.
import ipaddress
from .models import Song

def local_laptop_only(request: Request):
    if not settings.local_shared_mode:
        raise HTTPException(status_code=404, detail="Not found")
    host = request.client.host if request.client else ""
    try:
        if not ipaddress.ip_address(host).is_loopback:
            raise HTTPException(status_code=403, detail="Local laptop access only")
    except ValueError:
        raise HTTPException(status_code=403, detail="Local laptop access only")

@router.get("/api/local/songs")
def local_list_songs(_=Depends(local_laptop_only), db: Session = Depends(get_db)):
    return [song_payload(s) for s in db.query(Song).order_by(Song.title.asc()).all()]

@router.post("/api/local/songs", status_code=201)
def local_create_song(data: SongInput, _=Depends(local_laptop_only), db: Session = Depends(get_db)):
    song = Song(**data.model_dump())
    db.add(song)
    db.commit()
    db.refresh(song)
    return song_payload(song)

@router.put("/api/local/songs/{song_id}")
def local_update_song(song_id: int, data: SongInput, _=Depends(local_laptop_only), db: Session = Depends(get_db)):
    song = db.get(Song, song_id)
    if not song:
        raise HTTPException(404, "Song not found.")
    for key, value in data.model_dump().items():
        setattr(song, key, value)
    db.commit()
    db.refresh(song)
    return song_payload(song)

@router.delete("/api/local/songs/{song_id}")
def local_delete_song(song_id: int, _=Depends(local_laptop_only), db: Session = Depends(get_db)):
    song = db.get(Song, song_id)
    if not song:
        raise HTTPException(404, "Song not found.")
    db.delete(song)
    db.commit()
    return {"ok": True}

# Portable songbook backup: export one file and send it to the other laptop.
class SongbookImport(BaseModel):
    version: int = Field(default=1, ge=1, le=1)
    songs: list[SongInput] = Field(max_length=5000)

@router.get("/api/local/songbook/export")
def export_local_songbook(_=Depends(local_laptop_only), db: Session = Depends(get_db)):
    return {
        "format": "WorshipKeys",
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "songs": [song_payload(s) for s in db.query(Song).order_by(Song.title.asc()).all()],
    }

@router.post("/api/local/songbook/import")
def import_local_songbook(data: SongbookImport, _=Depends(local_laptop_only), db: Session = Depends(get_db)):
    # Import replaces the receiving laptop's current song list.
    db.query(Song).delete(synchronize_session=False)
    db.add_all([Song(**song.model_dump()) for song in data.songs])
    db.commit()
    return {"ok": True, "imported": len(data.songs)}