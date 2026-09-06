"""Authentication endpoints: register, login, me, logout."""

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password, verify_password, create_access_token, set_auth_cookie, clear_auth_cookie
from app.core.deps import get_current_user
from app.core.rate_limit import rate_limit
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.user import UserRead
import uuid
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_username(username: str) -> str:
    return username.strip()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit(limit=20, window=60, key_prefix="auth_register"))])
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    username = _normalize_username(payload.username)
    email = _normalize_email(str(payload.email))

    # Check duplicates explicitly for clean 409
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=409, detail="Username already taken")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    # Extra length guard (avoid huge payloads)
    if len(payload.password) > 128:
        raise HTTPException(status_code=400, detail="Password too long")

    hashed = hash_password(payload.password)
    user = User(
        username=username,
        email=email,
        password_hash=hashed,
        display_name=payload.display_name.strip() if payload.display_name else None,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        # Race condition fallback
        raise HTTPException(status_code=409, detail="Username or email already taken")

    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    return user


@router.post("/login", response_model=UserRead, dependencies=[Depends(rate_limit(limit=20, window=60, key_prefix="auth_login"))])
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    identifier = payload.identifier.strip()
    is_email = "@" in identifier

    user: User | None = None
    if is_email:
        email = _normalize_email(identifier)
        user = db.query(User).filter(User.email == email).first()
    else:
        username = _normalize_username(identifier)
        user = db.query(User).filter(User.username == username).first()

    # Uniform error to avoid user enumeration
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update updated_at touch handled by DB; no need explicit

    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    return user


def _ensure_demo_data(db, demo_user):
    # Idempotent demo seed — creates realistic IT community data if not exists
    from app.models.post import Post
    from app.models.social import PostLike, Comment
    from app.models.follow import Follow
    from app.models.story import Story
    from app.models.club import Club, ClubMember
    from app.models.club_channel import ClubChannel
    from app.models.club_message import ClubMessage
    from app.models.project import Project
    try:
        has_posts = db.query(Post).filter(Post.author_id == demo_user.id).first() is not None
        if has_posts:
            return
        # Create demo users for interactions if not exist
        demo_users = []
        for uname, email in [("alice_demo", "alice_demo@bailanysta.demo"), ("bob_demo", "bob_demo@bailanysta.demo")]:
            u = db.query(User).filter(User.username == uname).first()
            if not u:
                u = User(username=uname, email=email, password_hash=hash_password("Demo123!"), display_name=uname.replace("_", " ").title(), bio="Demo user for Bailanysta showcase")
                db.add(u); db.flush()
            demo_users.append(u)
        # Posts
        posts_data = [
            ("Запустил AI Resume Analyzer — Python + FastAPI + React. Делитесь фидбеком! #ai #python", ["ai", "python"]),
            ("Кто использует Rust для бэкенда? Плюсы/минусы vs Go? #rust #backend", ["rust", "backend"]),
            ("Наш клуб Python Kazakhstan — 200 участников! Присоединяйтесь 🚀 #python #community", ["python", "community"]),
        ]
        posts = []
        for content, _ in posts_data:
            p = Post(author_id=demo_user.id, content=content)
            db.add(p); db.flush()
            posts.append(p)
        # Likes/comments from demo users
        for p in posts[:2]:
            for u in demo_users:
                if not db.query(PostLike).filter(PostLike.post_id==p.id, PostLike.user_id==u.id).first():
                    db.add(PostLike(post_id=p.id, user_id=u.id))
                if not db.query(Comment).filter(Comment.post_id==p.id, Comment.author_id==u.id).first():
                    db.add(Comment(post_id=p.id, author_id=u.id, content="Круто! Спасибо за пост 🙌"))
        # Follows
        for u in demo_users:
            if not db.query(Follow).filter(Follow.follower_id==demo_user.id, Follow.following_id==u.id).first():
                db.add(Follow(follower_id=demo_user.id, following_id=u.id))
            if not db.query(Follow).filter(Follow.follower_id==u.id, Follow.following_id==demo_user.id).first():
                db.add(Follow(follower_id=u.id, following_id=demo_user.id))
        # Stories (1)
        from app.services.storage import save_story_media
        # Use text story if media not needed? Create simple text story via direct DB
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=24)
        if not db.query(Story).filter(Story.author_id==demo_user.id).first():
            s = Story(author_id=demo_user.id, media_url=None, media_type="text", text="Привет из демо! Bailanysta — место для IT комьюнити 💻", created_at=now, expires_at=expires)
            db.add(s)
        # Club + channel + messages
        club = db.query(Club).filter(Club.slug=="demo-club").first()
        if not club:
            club = Club(owner_id=demo_user.id, name="Demo Club", slug="demo-club", description="Демо клуб для проверяющих — IT комьюнити")
            db.add(club); db.flush()
            db.add(ClubMember(club_id=club.id, user_id=demo_user.id, role="owner"))
            for u in demo_users:
                if not db.query(ClubMember).filter(ClubMember.club_id==club.id, ClubMember.user_id==u.id).first():
                    db.add(ClubMember(club_id=club.id, user_id=u.id, role="member"))
            ch = ClubChannel(club_id=club.id, name="general", slug="general", description="Общий чат", position=0)
            db.add(ch); db.flush()
            for txt in ["Всем привет! 👋", "Как вам Bailanysta?", "Демо сообщения работают в реальном времени!"]:
                db.add(ClubMessage(channel_id=ch.id, author_id=demo_user.id, content=txt))
        # Projects
        if not db.query(Project).filter(Project.owner_id==demo_user.id).first():
            proj = Project(owner_id=demo_user.id, name="Bailanysta Demo", description="Демо проект — социальная платформа для IT комьюнити. Python, FastAPI, React, PostgreSQL.", technologies=["Python","FastAPI","React","PostgreSQL"], github_url="https://github.com/demo/bailanysta", demo_url="https://bailanysta.demo", status="in_progress", position=0)
            db.add(proj)
            proj2 = Project(owner_id=demo_user.id, name="AI Helper", description="AI помощник для анализа резюме. Демо.", technologies=["Python","AI","Docker"], github_url="https://github.com/demo/ai-helper", status="idea", position=1)
            db.add(proj2)
        db.commit()
    except Exception:
        db.rollback()
        # Don't fail demo login if seed fails
        pass

@router.post("/demo", response_model=UserRead, dependencies=[Depends(rate_limit(limit=10, window=60, key_prefix="demo"))])
def demo_login(response: Response, db: Session = Depends(get_db)):
    """Demo Mode — creates or returns demo account and logs in via normal cookie."""
    demo_username = "demo"
    demo_email = "demo@bailanysta.demo"
    demo_password = "Demo123!"
    user = db.query(User).filter(User.username == demo_username).first()
    if not user:
        # Create demo user
        user = User(username=demo_username, email=demo_email, password_hash=hash_password(demo_password), display_name="Demo User", bio="Демонстрационный аккаунт Bailanysta — IT community showcase. Нажмите 'Войти в демо' чтобы посмотреть платформу без регистрации.")
        db.add(user)
        db.commit()
        db.refresh(user)
        _ensure_demo_data(db, user)
    else:
        # Ensure data exists even if user already there
        _ensure_demo_data(db, user)
        # Ensure password is correct (in case changed)
        if not verify_password(demo_password, user.password_hash):
            user.password_hash = hash_password(demo_password)
            db.commit()
    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    return user


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, current_user: User = Depends(get_current_user)):
    clear_auth_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
